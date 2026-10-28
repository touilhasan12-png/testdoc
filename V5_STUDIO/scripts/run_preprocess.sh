#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y -qq ffmpeg >/dev/null
export MAMBA_ROOT_PREFIX="$RUNNER_TEMP/v5-mamba"
mkdir -p "$RUNNER_TEMP/micromamba"
curl -fsSL --retry 3 https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C "$RUNNER_TEMP/micromamba" bin/micromamba
MAMBA="$RUNNER_TEMP/micromamba/bin/micromamba"
"$MAMBA" --version
"$MAMBA" create -y -q -n pilot -c conda-forge python=3.11 pip
"$MAMBA" run -n pilot python -m pip install -q --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
"$MAMBA" run -n pilot python -m pip install -q --no-cache-dir 'rembg[cpu]' faster-whisper stable-ts 'numpy<2.0' Pillow
# stable-ts may otherwise pull a CUDA-linked torchaudio wheel from PyPI.
"$MAMBA" run -n pilot python -m pip install -q --force-reinstall --no-deps torchaudio --index-url https://download.pytorch.org/whl/cpu
"$MAMBA" run -n pilot python "$V5_ROOT/scripts/preprocess.py"
