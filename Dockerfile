FROM archlinux:latest

RUN pacman -Syu --noconfirm \
    python python-pip git shellcheck figlet xorg-xinput && \
    pacman -Scc --noconfirm

RUN pip install --no-cache-dir black flake8 pytest

WORKDIR /workspace
