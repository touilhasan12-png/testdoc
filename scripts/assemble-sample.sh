#!/usr/bin/env bash
# Assembles the 300 s sample from the rendered frame chunks.
#  1) stream-copy concat of parts/part-*.mp4 (no re-encode of video)
#  2) audio mix: VO 01-09 at their measured offsets + pad + SFX
#  3) verification: duration, frame count, audio presence, head/middle/tail luma
set -euo pipefail
mkdir -p out/final
ls parts/part-*.mp4 | sort -V > out/parts.txt
: > out/concat.txt
while read -r p; do echo "file '$PWD/$p'" >> out/concat.txt; done < out/parts.txt
ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i out/concat.txt -c copy out/video.mp4

mapfile -t CUES < <(node -e 'for (const c of require("./src/data/vo-cues.json")) console.log(c.file + "|" + c.startMs)')
ARGS=(-y -hide_banner -loglevel error -i out/video.mp4 -i out/audio/pad.wav -i out/audio/sfx.wav)
FILTER=""
LABELS=""
idx=3
for c in "${CUES[@]}"; do
  file="${c%|*}"; ms="${c#*|}"
  ARGS+=(-i "$file")
  FILTER+="[${idx}:a]adelay=${ms}:all=1[v${idx}];"
  LABELS+="[v${idx}]"
  idx=$((idx + 1))
done
N_IN=$((idx - 1))
FILTER+="[1:a]volume=1.0[pad];[2:a]volume=1.0[sfx];[pad][sfx]${LABELS}amix=inputs=${N_IN}:duration=longest:normalize=0,aformat=sample_rates=48000:channel_layouts=stereo[a]"
OUT=out/final/testdoc-sample-300s.mp4
ffmpeg "${ARGS[@]}" -filter_complex "$FILTER" -map 0:v:0 -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"

echo "== verification =="
ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=codec_name,width,height,avg_frame_rate,nb_read_frames -of default=nw=1 "$OUT"
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,channels,sample_rate -of default=nw=1 "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$OUT")
FRAMES=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nw=1:nk=1 "$OUT")
python3 - "$DUR" "$FRAMES" <<'PY'
import sys
dur, frames = float(sys.argv[1]), int(sys.argv[2])
ok = abs(dur - 300.0) < 0.2 and frames == 9000
print(f"duration={dur:.3f}s frames={frames} -> {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
PY
for n in 0 4500 8999; do
  Y=$(ffmpeg -hide_banner -i "$OUT" -vf "select=eq(n\,${n}),signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" -frames:v 1 -f null - 2>/dev/null | grep -o 'YAVG=[0-9.]*' | head -1 || true)
  echo "frame ${n}: ${Y:-unavailable}"
done
ffmpeg -hide_banner -i "$OUT" -af volumedetect -vn -sn -dn -f null - 2>&1 | grep -E "mean_volume|max_volume" || true
ls -la out/final/
