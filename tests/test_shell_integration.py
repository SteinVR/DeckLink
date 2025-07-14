import os
import subprocess

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(REPO_DIR, "main.sh")


def run_shell(cmd, **env):
    env_vars = os.environ.copy()
    env_vars.update(env)
    return subprocess.run(
        ["/bin/bash", "-c", cmd], capture_output=True, text=True, env=env_vars
    )


def test_check_dependencies_failure(tmp_path):
    env = {"PATH": str(tmp_path)}
    result = run_shell(f"source {SCRIPT}; check_dependencies", **env)
    assert result.returncode != 0


def test_pid_file_cleanup(tmp_path):
    env = {"PATH": os.environ["PATH"]}
    cmd = (
        f"source {SCRIPT};"
        "FIGLET_CMD=echo;"
        "check_dependencies(){ :; };"
        "set_brightness_to_minimum(){ :; };"
        "restore_brightness(){ :; };"
        "disable_sleep(){ :; };"
        "reenable_sleep(){ :; };"
        "block_until_press_on_target(){ :; };"
        "python3(){ :; };"
        "run_as_root;"
        "test ! -f /tmp/decklink.pid"
    )
    result = run_shell(cmd, **env)
    assert result.returncode == 0
