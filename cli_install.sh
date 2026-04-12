#!/usr/bin/env bash
# Installs the 'macros' command into ~/.local/bin
# Run once: bash cli_install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"
WRAPPER="$INSTALL_DIR/macros"

echo "Macro Tracker CLI Installer"
echo "==========================="

# 1. Install Python deps
echo ""
echo "Installing Python dependencies..."
pip3 install --user --quiet \
  "gspread>=6.0.0" \
  "google-auth>=2.22.0" \
  "google-auth-oauthlib>=1.1.0" \
  "google-auth-httplib2>=0.2.0" \
  "mcp>=1.0.0" \
  "tabulate>=0.9.0" \
  "colorama>=0.4.6" \
  "flask>=3.0.0" \
  "flask-cors>=4.0.0"
echo "Dependencies installed."

# 2. Create ~/.local/bin if needed
mkdir -p "$INSTALL_DIR"

# 3. Write wrapper script
cat > "$WRAPPER" << EOF
#!/usr/bin/env bash
exec python3 "${SCRIPT_DIR}/macros.py" "\$@"
EOF
chmod +x "$WRAPPER"
echo "Installed: $WRAPPER"

# 4. Check PATH
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
  echo ""
  echo "NOTE: $INSTALL_DIR is not in your PATH."
  echo "Add this to your ~/.bashrc or ~/.zshrc:"
  echo ""
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  echo ""
  echo "Then reload: source ~/.bashrc"
else
  echo ""
  echo "Installation complete! Test with:"
  echo "  macros today"
  echo "  macros staples"
fi
