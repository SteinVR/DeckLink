#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTDIR="${DESTDIR:-/usr/share/decklink}"
PYPROJECT_FILE="${PYPROJECT_FILE:-$DIR/pyproject.toml}"
POLKIT_DIR="${POLKIT_DIR:-/etc/polkit-1/rules.d}"

pacman_install() {
    if command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --noconfirm "$@"
    else
        echo "pacman not found. Please install $* manually." >&2
    fi
}

pip_install() {
    local pipcmd
    pipcmd=$(command -v pip3 || command -v pip || true)
    if [ -n "$pipcmd" ]; then
        sudo "$pipcmd" install --break-system-packages "$@"
    else
        echo "pip not found. Skipping Python dependencies." >&2
    fi
}

parse_pyproject_deps() {
    python3 - "$PYPROJECT_FILE" <<'EOF'
import sys, tomllib
path = sys.argv[1]
try:
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    deps = data.get('project', {}).get('dependencies', [])
    print(' '.join(deps))
except Exception:
    pass
EOF
}

check_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python 3 is required." >&2
        exit 1
    fi
    if ! command -v pip3 >/dev/null 2>&1 && ! command -v pip >/dev/null 2>&1; then
        echo "pip is required." >&2
        exit 1
    fi
    if ! python3 -c 'import usb' 2>/dev/null; then
        echo "Warning: Python USB dependencies missing" >&2
    fi
}

install_files() {
    if [ -d "$DESTDIR" ]; then
        echo "Updating existing installation at $DESTDIR"
        rm -rf "$DESTDIR"
    fi
    mkdir -p "$DESTDIR"
    cp -r "$DIR/decklink_app" "$DESTDIR/"
    install -m755 "$DIR/main.sh" "$DESTDIR/main.sh"
}

install_polkit() {
    if [ -d "$POLKIT_DIR" ]; then
        sudo cp "$DIR/policy/90-decklink.rules" "$POLKIT_DIR/"
    fi
}

install_vdf() {
    local cfg="$HOME/.steam/steam/controller_config"
    mkdir -p "$cfg"
    cp "$DIR/decklink_app/game_actions_480.vdf" "$cfg/"
}

main() {
    check_python
    pacman_install xorg-xinput figlet
    deps="$(parse_pyproject_deps)"
    if [ -n "$deps" ]; then
        # shellcheck disable=SC2086
        pip_install $deps
    fi
    install_files
    install_polkit
    install_vdf
    echo "DeckLink installed to $DESTDIR"
}

main "$@"
