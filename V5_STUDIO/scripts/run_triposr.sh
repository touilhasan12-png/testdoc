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
# Inspect the reconstruction as an actual render, rather than trusting inference.
cp "$V5_OUT/ship_triposr.glb" "$V5_ROOT/public/private/ship_triposr.glb"
sudo apt-get update -qq
sudo apt-get install -y -qq blender python3-numpy >/dev/null
if blender -b -t 4 --python-use-system-env --python-exit-code 1 --python "$V5_ROOT/scripts/blender_ship.py" > "$V5_OUT/blender_ship.log" 2>&1; then
 echo 'PASS Blender rendered revised TripoSR mesh.'
else
 printf '{"ok":false,"error":"Blender ship rendering failed; see blender_ship.log"}\n' > "$V5_OUT/blender_ship_status.json"
 echo 'FAILED Blender mesh preview.'
fi
