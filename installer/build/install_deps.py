"""Cross-install Windows wheels for `requirements.txt` into the embedded
Python's `Lib/site-packages`.

Pip's `--platform win_amd64 --python-version 311 --prefer-binary` flags
let us download Windows wheels from any host (Linux or Windows). We then
install them with `--target` to land them inside the embed dist's
site-packages.

Limitations:
- Top-level deps with C extensions (python-rtmidi, Pillow, psutil) MUST have
  a cp311-win_amd64 wheel on PyPI.
- Pure-Python deps (transitive: proxy-tools, etc.) without wheels will install
  from sdist — `--prefer-binary` (not `--only-binary=:all:`) allows this.
"""
import subprocess
import sys
from pathlib import Path


def install_windows_wheels(
    requirements_file: Path,
    target_site_packages: Path,
    python_version: str = "311",
    pip_executable: str = sys.executable,
) -> None:
    """Install wheels into target_site_packages for Windows amd64.

    Uses the host's pip (cross-arch) — works equally well on Linux and Windows
    since we explicitly pin the platform.

    Raises subprocess.CalledProcessError if pip exits non-zero.
    """
    target_site_packages.mkdir(parents=True, exist_ok=True)

    cmd = [
        pip_executable,
        "-m", "pip",
        "install",
        "--target", str(target_site_packages),
        "--platform", "win_amd64",
        "--python-version", python_version,
        "--prefer-binary",
        "--upgrade",
        "-r", str(requirements_file),
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cross-install Windows wheels.")
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True,
                        help="Path to <embed>/Lib/site-packages")
    parser.add_argument("--python-version", default="311")
    args = parser.parse_args()
    install_windows_wheels(
        requirements_file=args.requirements,
        target_site_packages=args.target,
        python_version=args.python_version,
    )
    print(f"Wheels installed to {args.target}")
