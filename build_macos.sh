#!/bin/zsh

set -euo pipefail

APP_NAME="OsmosePresets"
BUNDLE_ID="uk.co.carlcaulkett.osmosepresets"

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"

APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

PYINSTALLER_BINARY="$DIST_DIR/$APP_NAME"
BUNDLED_BINARY="$RESOURCES_DIR/$APP_NAME"
RUNNER="$RESOURCES_DIR/$APP_NAME.command"
LAUNCHER="$MACOS_DIR/${APP_NAME}Launcher"

cd "$PROJECT_DIR"

echo "→ Reading project version..."

VERSION="$(
   uv run python - <<'PY'
import tomllib
from pathlib import Path

with Path("pyproject.toml").open("rb") as f:
   data = tomllib.load(f)

print(data["project"]["version"])
PY
)"

echo "  Version: $VERSION"

echo
echo "→ Cleaning previous build..."

rm -rf "$BUILD_DIR" "$DIST_DIR"
rm -f "$PROJECT_DIR/$APP_NAME.spec"

echo
echo "→ Building standalone executable..."

uv run pyinstaller \
   --name "$APP_NAME" \
   --onefile \
   --hidden-import=mido.backends.rtmidi \
   --collect-all=rtmidi \
   --add-data "src/osmose_presets/OsmosePresets.json:osmose_presets" \
   --add-data "src/osmose_presets/osmose_presets.tcss:." \
   src/osmose_presets/app.py

echo
echo "→ Creating macOS application bundle..."

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

mv "$PYINSTALLER_BINARY" "$BUNDLED_BINARY"

chmod +x "$BUNDLED_BINARY"

echo
echo "→ Creating Terminal runner..."

cat > "$RUNNER" <<'ZSH'
#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXECUTABLE="$SCRIPT_DIR/OsmosePresets"

TARGET_TTY="$(tty)"

clear

"$EXECUTABLE"
STATUS=$?

/usr/bin/osascript - "$TARGET_TTY" <<'APPLESCRIPT'
on run argv
   set targetTTY to item 1 of argv

   tell application "Terminal"
      repeat with terminalWindow in windows
         repeat with terminalTab in tabs of terminalWindow
            if tty of terminalTab is targetTTY then
               close terminalWindow
               return
            end if
         end repeat
      end repeat
   end tell
end run
APPLESCRIPT

exit $STATUS
ZSH

chmod +x "$RUNNER"

echo
echo "→ Creating application launcher..."

cat > "$LAUNCHER" <<'ZSH'
#!/bin/zsh

CONTENTS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNNER="$CONTENTS_DIR/Resources/OsmosePresets.command"

exec /usr/bin/open -a Terminal "$RUNNER"
ZSH

chmod +x "$LAUNCHER"

echo
echo "→ Creating Info.plist..."

cat > "$CONTENTS_DIR/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
   "http://www.apple.com/DTDs/PropertyList-1.0.dtd">

<plist version="1.0">
<dict>
   <key>CFBundleName</key>
   <string>$APP_NAME</string>

   <key>CFBundleDisplayName</key>
   <string>$APP_NAME</string>

   <key>CFBundleIdentifier</key>
   <string>$BUNDLE_ID</string>

   <key>CFBundleVersion</key>
   <string>$VERSION</string>

   <key>CFBundleShortVersionString</key>
   <string>$VERSION</string>

   <key>CFBundlePackageType</key>
   <string>APPL</string>

   <key>CFBundleExecutable</key>
   <string>${APP_NAME}Launcher</string>

   <key>LSMinimumSystemVersion</key>
   <string>13.0</string>

   <key>NSAppleEventsUsageDescription</key>
   <string>OsmosePresets uses Terminal to display its Textual interface.</string>
</dict>
</plist>
EOF

echo
echo "→ Validating Info.plist..."

plutil -lint "$CONTENTS_DIR/Info.plist"

echo
echo "→ Ad-hoc signing application..."

codesign \
   --force \
   --deep \
   --sign - \
   "$APP_BUNDLE"

echo
echo "→ Verifying signature..."

codesign \
   --verify \
   --deep \
   --strict \
   --verbose=2 \
   "$APP_BUNDLE"

echo
echo "✓ Build complete"
echo
echo "Application:"
echo "  $APP_BUNDLE"
echo
echo "Launch with:"
echo "  open \"$APP_BUNDLE\""
