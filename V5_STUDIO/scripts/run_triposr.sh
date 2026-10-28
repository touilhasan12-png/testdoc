#!/usr/bin/env bash
set -euo pipefail
export MAMBA_ROOT_PREFIX="$RUNNER_TEMP/v5-mamba"
mkdir -p "$RUNNER_TEMP/micromamba"
curl -fsSL --retry 3 https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C "$RUNNER_TEMP/micromamba" bin/micromamba
MAMBA="$RUNNER_TEMP/micromamba/bin/micromamba"
"$MAMBA" create -y -q -n reconstruction -c conda-forge python=3.11 pip
"$MAMBA" run -n reconstruction python -m pip install -q --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
"$MAMBA" run -n reconstruction python -m pip install -q --no-cache-dir 'numpy<2' 'transformers==4.35.0' 'huggingface-hub<0.20' 'omegaconf==2.3.0' 'einops==0.7.0' 'trimesh==4.0.5' imageio 'rembg[cpu]' scikit-image
export TRIPOSR_DIR="$RUNNER_TEMP/TripoSR" TRIPOSR_MODEL="$RUNNER_TEMP/TripoSR_model"
git clone -q --depth 1 https://github.com/VAST-AI-Research/TripoSR.git "$TRIPOSR_DIR"
mkdir -p "$TRIPOSR_MODEL"
curl -fsSL --retry 2 -o "$TRIPOSR_MODEL/config.yaml" https://huggingface.co/stabilityai/TripoSR/resolve/main/config.yaml
curl -fsSL --retry 2 -o "$TRIPOSR_MODEL/model.ckpt" https://huggingface.co/stabilityai/TripoSR/resolve/main/model.ckpt
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
# The time limit bounds CPU-only inference; on failure the workflow records it.
timeout 1200 "$MAMBA" run -n reconstruction python "$V5_ROOT/scripts/triposr_cpu.py"
