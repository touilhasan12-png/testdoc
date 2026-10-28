#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y -qq blender ffmpeg python3-numpy python3-pil libcairo2-dev libpango1.0-dev pkg-config >/dev/null
python -m venv "$RUNNER_TEMP/manim-venv"
"$RUNNER_TEMP/manim-venv/bin/pip" install -q --no-cache-dir manim
mkdir -p "$RUNNER_TEMP/geodata" "$V5_OUT/manim"
curl -fsSL --retry 3 -o "$RUNNER_TEMP/geodata/countries.zip" https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip
unzip -oq "$RUNNER_TEMP/geodata/countries.zip" -d "$RUNNER_TEMP/geodata"
# mapshaper actually filters and simplifies real Natural Earth country outlines.
npx --yes mapshaper "$RUNNER_TEMP/geodata/ne_50m_admin_0_countries.shp" -filter "ADM0_A3 == 'ESP' || ADM0_A3 == 'PRT'" -simplify 20% keep-shapes -o format=shapefile "$RUNNER_TEMP/geodata/iberia.shp"
export IBERIA_SHP="$RUNNER_TEMP/geodata/iberia.shp" BLENDERGIS_DIR="$RUNNER_TEMP/BlenderGIS"
git clone -q --depth 1 https://github.com/domlysz/BlenderGIS.git "$BLENDERGIS_DIR"
if blender -b -t 4 --python-use-system-env --python-exit-code 1 --python "$V5_ROOT/scripts/blendergis_layer.py" > "$V5_OUT/blender.log" 2>&1; then
 echo 'PASS Blender/BlenderGIS.'
else
 printf '{"ok":false,"error":"BlenderGIS import or rendering failed; see blender.log"}\n' > "$V5_OUT/blendergis_status.json"
 echo 'FAILED Blender/BlenderGIS; details in encrypted diagnostic.'
fi
if blender -b -t 4 --python-use-system-env --python-exit-code 1 --python "$V5_ROOT/scripts/blender_ship.py" > "$V5_OUT/blender_ship.log" 2>&1; then
 echo 'PASS Blender ship rendering.'
else
 printf '{"ok":false,"error":"Blender ship rendering failed; see blender_ship.log"}\n' > "$V5_OUT/blender_ship_status.json"
 echo 'FAILED Blender ship rendering.'
fi
if "$RUNNER_TEMP/manim-venv/bin/manim" -ql -r 960,540 --fps 24 -t --format=webm --media_dir "$V5_OUT/manim" "$V5_ROOT/scripts/compass_manim.py" NavigationOrbit > "$V5_OUT/manim.log" 2>&1; then
 movie=$(find "$V5_OUT/manim" -name '*.webm' -type f | head -1)
 if [ -n "$movie" ];then cp "$movie" "$V5_OUT/navigation_orbit.webm";fi
 printf '{"ok":true,"detail":"Animated navigation orbit rendered by Manim"}\n' > "$V5_OUT/manim_status.json"
 echo 'PASS Manim.'
else
 printf '{"ok":false,"error":"Manim animation failed; see manim.log"}\n' > "$V5_OUT/manim_status.json"
 echo 'FAILED Manim; details in encrypted diagnostic.'
fi
printf '{"ok":true,"detail":"Natural Earth country polygons filtered and simplified with mapshaper"}\n' > "$V5_OUT/mapshaper_status.json"
