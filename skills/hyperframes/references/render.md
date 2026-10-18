# HyperFrames Rendering Pipeline

Local rendering workflow, toolchain prerequisites, and execution options.

## Local Prerequisites

HyperFrames rendering requires modern Node and local media toolchains:

- **Node.js ≥22** (`node -v` must report `v22.0.0` or higher)
- **FFmpeg** on system PATH (`which ffmpeg`)
- **Headless Chromium / Chrome** (managed automatically by Puppeteer or system browser)

Verification check:
```bash
node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)' && which ffmpeg
```
If Node <22 or FFmpeg is absent: report `NOT_CONFIGURED` (never report false PASS).

## Primary Rendering Path (Official CLI)

The primary and recommended workflow uses the official `@hyperframes/cli`:

### 1. Initialize Project Directory
```bash
npx hyperframes init <dir>
```

### 2. Live Interactive Preview
```bash
npx hyperframes preview
```

### 3. Production Deterministic Render
```bash
npx hyperframes render [dir] -o <path> -f <fps> -q <quality> [--format mp4|webm|mov|gif|png-sequence]
```

#### Common Invocations:
```bash
# High quality 60fps landscape MP4
npx hyperframes render . -o renders/launch.mp4 -f 60 -q delivery

# Render specific composition file
npx hyperframes render . -c compositions/intro.html -o renders/intro.mp4

# Transparent ProRes MOV overlay
npx hyperframes render . -o renders/overlay.mov --format mov

# Transparent WebM overlay
npx hyperframes render . -o renders/overlay.webm --format webm

# Animated GIF for PRs / docs at 15fps
npx hyperframes render . -o renders/demo.gif --format gif -f 15 --gif-loop 0

# Docker-isolated render (identical font and Chromium baseline)
npx hyperframes render . -o renders/reproducible.mp4 --docker
```

## Explicit Fallback: Manual CDP & FFmpeg

If the official CLI cannot be executed in the environment, use direct Headless Chromium frame stepping as a secondary fallback:

1. Calculate total frame count: `TOTAL_FRAMES = FPS * DURATION_SECONDS`.
2. Connect to Chromium via DevTools Protocol (`Page.captureScreenshot`), seek timeline to each step, and save frames sequentially to `./frames/frame_%05d.png`.
3. Encode frames using FFmpeg:

```bash
# Visual lossless H.264 MP4 encode
ffmpeg -y -framerate 60 -i frames/frame_%05d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  output.mp4

# Multiplexing background audio
ffmpeg -y -framerate 60 -i frames/frame_%05d.png -i audio.mp3 \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest \
  output.mp4
```
