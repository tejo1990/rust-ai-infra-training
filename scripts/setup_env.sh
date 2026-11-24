#!/usr/bin/env bash
# Check (or optionally install) the Linux/WSL2 toolchain for the 4-week training.
# Usage:
#   bash scripts/setup_env.sh           # read-only audit (safe default)
#   bash scripts/setup_env.sh --install # installs rustup nightly+miri and uv if missing

set -euo pipefail

DO_INSTALL=0
if [[ "${1:-}" == "--install" ]]; then
  DO_INSTALL=1
fi

echo "=== Rust Systems + Python AI Infra Toolchain Audit ==="

check_cmd() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf "[OK]      %-10s -> %s\n" "$name" "$("$name" --version 2>&1 | head -n 1)"
    return 0
  else
    printf "[MISSING] %-10s\n" "$name"
    return 1
  fi
}

check_cmd git || true
check_cmd python3 || true
HAS_RUST=0
check_cmd rustc && HAS_RUST=1 || true
check_cmd cargo || true
HAS_UV=0
check_cmd uv && HAS_UV=1 || true
check_cmd gh || echo "          (optional: scripts/pick_shadow_pr.py works without gh)"

if [[ "$HAS_RUST" -eq 1 ]]; then
  if rustup toolchain list 2>/dev/null | grep -q "^nightly"; then
    if rustup component list --toolchain nightly --installed 2>/dev/null | grep -q "^miri"; then
      echo "[OK]      miri       -> nightly miri installed"
    else
      echo "[MISSING] miri       -> run: rustup +nightly component add miri"
      if [[ "$DO_INSTALL" -eq 1 ]]; then
        rustup +nightly component add miri
      fi
    fi
  else
    echo "[MISSING] nightly    -> run: rustup toolchain install nightly --component miri"
    if [[ "$DO_INSTALL" -eq 1 ]]; then
      rustup toolchain install nightly --component miri
    fi
  fi
elif [[ "$DO_INSTALL" -eq 1 ]]; then
  echo "Installing rustup + stable + nightly(miri)..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  # shellcheck disable=SC1091
  source "$HOME/.cargo/env"
  rustup toolchain install nightly --component miri
fi

if [[ "$HAS_UV" -eq 0 && "$DO_INSTALL" -eq 1 ]]; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo ""
echo "Recommended upstream clone directory (gitignored): mkdir -p repos"
echo "  git clone --filter=blob:none https://github.com/tokio-rs/tokio.git repos/tokio"
echo "  git clone --filter=blob:none https://github.com/vllm-project/vllm.git repos/vllm"
echo "  git clone --filter=blob:none https://github.com/sgl-project/sglang.git repos/sglang"
