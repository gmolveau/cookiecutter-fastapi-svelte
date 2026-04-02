import subprocess
import sys
from pathlib import Path

backend = Path("backend")
frontend = Path("frontend")

print("\n--- Installing backend dependencies ---")
result = subprocess.run(["uv", "sync"], cwd=backend)
if result.returncode != 0:
    print(
        "ERROR: uv sync failed. Run it manually: cd backend && uv sync", file=sys.stderr
    )
    sys.exit(result.returncode)

print("\n--- Installing frontend dependencies ---")
result = subprocess.run(["just", "install-dev"], cwd=frontend)
if result.returncode != 0:
    print("ERROR: pnpm failed.", file=sys.stderr)
    sys.exit(result.returncode)

print("\n--- Setting up env ---")
result = subprocess.run(["just", "init-env"])
if result.returncode != 0:
    print("ERROR: init-env failed.", file=sys.stderr)
    sys.exit(result.returncode)

print()
print("Done")
print("Next steps:")
print("  cd backend && just migrate")
print("  just dev-up")
