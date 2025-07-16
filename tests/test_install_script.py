import os
from pathlib import Path
import subprocess


def run_shell(cmd, **env):
    env_vars = os.environ.copy()
    env_vars.update(env)
    return subprocess.run(
        ["/bin/bash", "-c", cmd], capture_output=True, text=True, env=env_vars
    )


REPO_DIR = Path(__file__).resolve().parents[1]
SCRIPT = REPO_DIR / "install.sh"


def make_stub(dir_path: Path, name: str, content: str) -> Path:
    path = dir_path / name
    path.write_text(content)
    path.chmod(0o755)
    return path


def test_install_copies_files(tmp_path):
    dest = tmp_path / "install"
    log_pacman = tmp_path / "pacman.log"
    log_pip = tmp_path / "pip.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    make_stub(bin_dir, "sudo", "#!/bin/bash\n\n$@")
    make_stub(bin_dir, "pacman", f'#!/bin/bash\necho "$@" >> {log_pacman}\n')
    make_stub(bin_dir, "pip3", f'#!/bin/bash\necho "$@" >> {log_pip}\n')

    home = tmp_path / "home"
    polkit = tmp_path / "polkit"
    env = {
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "DESTDIR": str(dest),
        "HOME": str(home),
        "POLKIT_DIR": str(polkit),
    }
    result = run_shell(str(SCRIPT), **env)
    assert result.returncode == 0

    main_sh = dest / "main.sh"
    assert main_sh.exists()
    assert os.access(main_sh, os.X_OK)
    assert (dest / "decklink_app").is_dir()
    assert not (dest / "source_Deckpad").exists()
    assert not (dest / "source_GadgetDeck").exists()

    pip_log = log_pip.read_text()
    assert "xorg-xinput" in log_pacman.read_text()
    assert "steamworks" in pip_log
    assert "usb-gadget" in pip_log
    assert "python-hid-parser" in pip_log

    assert (
        home / ".steam/steam/controller_config/game_actions_480.vdf"
    ).exists()
    assert (polkit / "90-decklink.rules").exists()


def test_install_overwrites_existing(tmp_path):
    dest = tmp_path / "install"
    dest.mkdir()
    (dest / "oldfile").write_text("old")
    log_pacman = tmp_path / "pacman.log"
    log_pip = tmp_path / "pip.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_stub(bin_dir, "sudo", "#!/bin/bash\n\n$@")
    make_stub(bin_dir, "pacman", f'#!/bin/bash\necho "$@" >> {log_pacman}\n')
    make_stub(bin_dir, "pip3", f'#!/bin/bash\necho "$@" >> {log_pip}\n')

    env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "DESTDIR": str(dest)}
    result = run_shell(str(SCRIPT), **env)
    assert result.returncode == 0
    assert not (dest / "oldfile").exists()
    assert log_pacman.exists()


def test_warns_on_missing_usb(tmp_path):
    dest = tmp_path / "install"
    log_pacman = tmp_path / "pacman.log"
    log_pip = tmp_path / "pip.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    make_stub(bin_dir, "sudo", "#!/bin/bash\n\n$@")
    make_stub(bin_dir, "pacman", f'#!/bin/bash\necho "$@" >> {log_pacman}\n')
    make_stub(bin_dir, "pip3", f'#!/bin/bash\necho "$@" >> {log_pip}\n')

    env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "DESTDIR": str(dest)}
    result = run_shell(str(SCRIPT), **env)
    assert result.returncode == 0
    assert "Warning: Python USB dependencies missing" in result.stderr
