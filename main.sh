#!/bin/bash

set -o pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR" || exit

FIGLET_CMD="figlet"

prepare_fullscreen() {
    clear
    for _ in {1..10}; do echo ""; done
}

show_prompt() {
    local prompt=$1
    local style=${2:-banner}
    if [[ $FIGLET_CMD == figlet ]]; then
        figlet -c -w 180 -f "$style" -k -- "$prompt"
    else
        echo "$prompt"
    fi
    echo
    echo
    echo
}

block_until_mouse_click() {
    echo -e "\e[?1000h"
    read -r -n 12
}

block_until_press_on_target() {
    local TARGET_X_MIN=26500
    local TARGET_Y_MIN=25000
    local TARGET_X_MAX=37000
    local TARGET_Y_MAX=42000
    local TOUCHSCREEN_ID
    TOUCHSCREEN_ID=$(xinput --list 2>/dev/null | grep -i -m 1 'touch' | grep -o 'id=[0-9]\+' | grep -o '[0-9]\+')
    local touch_x=0
    local touch_y=0
    if [[ -z $TOUCHSCREEN_ID ]]; then
        block_until_mouse_click
        return
    fi
    while (( touch_x < TARGET_X_MIN )) || (( touch_x > TARGET_X_MAX )) || (( touch_y < TARGET_Y_MIN )) || (( touch_y > TARGET_Y_MAX )); do
        _show_run_prompt
        block_until_mouse_click
        local touch_state
        touch_state=$(xinput --query-state "$TOUCHSCREEN_ID" 2>/dev/null)
        if [[ $touch_state =~ valuator\[0]=([0-9]*) ]]; then
            touch_x=${BASH_REMATCH[1]}
        fi
        if [[ $touch_state =~ valuator\[1]=([0-9]*) ]]; then
            touch_y=${BASH_REMATCH[1]}
        fi
        if [[ -z $touch_state ]]; then
            # Fallback if coordinates unavailable
            break
        fi
    done
}

disable_sleep() {
    sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target >/dev/null 2>&1
}

reenable_sleep() {
    sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target >/dev/null 2>&1
}

brightness_file=/sys/class/backlight/amdgpu_bl0/brightness

set_brightness_to_minimum() {
    if [ -w "$brightness_file" ]; then
        cat "$brightness_file" >/tmp/brightness_bak 2>/dev/null || true
        echo 0 >"$brightness_file" 2>/dev/null || true
        chmod 444 "$brightness_file" 2>/dev/null || true
    fi
}

restore_brightness() {
    if [ -w "$brightness_file" ] || [ -r "$brightness_file" ]; then
        chmod 666 "$brightness_file" 2>/dev/null || true
        if [ -f /tmp/brightness_bak ]; then
            cat /tmp/brightness_bak >"$brightness_file" 2>/dev/null || true
            rm /tmp/brightness_bak
        fi
    fi
}

_show_run_prompt() {
    local battery
    battery=$(cat /sys/class/power_supply/BAT1/capacity)
    prepare_fullscreen
    show_prompt "Press to Quit"
    show_prompt "-> O <-"
    show_prompt "$battery %"
}

_do_run_prompt() {
    while true; do
        sleep 10
        _show_run_prompt
    done
}

run_prompt_start() {
    _do_run_prompt &
    echo $! >/tmp/run_prompt_pid
}

run_prompt_stop() {
    if [ -f /tmp/run_prompt_pid ]; then
        kill -s SIGKILL "$(cat /tmp/run_prompt_pid)" 2>/dev/null
        rm /tmp/run_prompt_pid
    fi
}

check_dependencies() {
    if ! command -v xinput >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
        echo "Missing required dependencies (python3 or xinput)." >&2
        exit 1
    fi
    if ! command -v figlet >/dev/null 2>&1; then
        FIGLET_CMD="echo"
    fi
}

run_as_root() {
    check_dependencies
    $FIGLET_CMD "Starting DeckLink..."
    set_brightness_to_minimum
    disable_sleep
    if ! python3 decklink_app/main_app.py setup; then
        restore_brightness
        reenable_sleep
        return 1
    fi
    (
        python3 decklink_app/main_app.py run &
        echo $! >/tmp/decklink.pid
        wait $!
    ) &
    run_prompt_start
    block_until_press_on_target
    run_prompt_stop
    if [ -f /tmp/decklink.pid ]; then
        kill "$(cat /tmp/decklink.pid)" 2>/dev/null
        wait "$(cat /tmp/decklink.pid 2>/dev/null)"
        rm /tmp/decklink.pid
    fi
    python3 decklink_app/main_app.py stop
    python3 decklink_app/main_app.py destroy
    restore_brightness
    reenable_sleep
    $FIGLET_CMD "DeckLink Stopped"
}

prepare_fullscreen
show_prompt "DeckLink requires root privileges" big
show_prompt "(screen will dim)" big
xhost local:root >/dev/null
FUNC=$(declare -f run_as_root)
sudo bash -c "$FUNC; run_as_root"

