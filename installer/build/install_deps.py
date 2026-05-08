"""Cross-install Windows wheels for `requirements.txt` into the embedded
Python's `Lib/site-packages`.

Pip requires `--only-binary=:all:` whenever `--platform`/`--python-version`
are used. We do TWO passes:

1. Try to install everything from wheels (`--only-binary=:all:`). This handles
   the typical case: deps with published cp311-win_amd64 wheels.
2. If pass 1 fails because some pure-Python transitive dep is sdist-only
   (e.g., proxy-tools), fall back to a per-package retry with `--no-deps`
   for each requirement — which downloads sdists without enforcing platform
   constraints on transitive deps.

Limitations:
- Top-level deps with C extensions MUST have cp311-win_amd64 wheels.
- Sdist-only pure-Python deps will install from source on the host (Linux),
  which is fine since pure-Python deps are platform-independent.
"""
import subprocess
import sys
from pathlib import Path


def _try_only_binary(
    pip_executable: str,
    requirements_file: Path,
    target_site_packages: Path,
    python_version: str,
) -> bool:
    """First pass: strict wheels-only cross-install. Returns True if it succeeded."""
    cmd = [
        pip_executable,
        "-m", "pip",
        "install",
        "--target", str(target_site_packages),
        "--platform", "win_amd64",
        "--python-version", python_version,
        "--only-binary=:all:",
        "--upgrade",
        "-r", str(requirements_file),
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def _fallback_per_package(
    pip_executable: str,
    requirements_file: Path,
    target_site_packages: Path,
    python_version: str,
) -> None:
    """Second pass: install each requirement separately. For each one, try
    binary-only first; if pip refuses, retry without platform constraints
    (sdist install on the host, which works for pure-Python deps).
    """
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    for req in requirements:
        binary_cmd = [
            pip_executable, "-m", "pip", "install",
            "--target", str(target_site_packages),
            "--platform", "win_amd64",
            "--python-version", python_version,
            "--only-binary=:all:",
            "--upgrade",
            req,
        ]
        if subprocess.run(binary_cmd).returncode == 0:
            continue
        # Fallback: install without platform constraints. Pure-Python packages
        # work this way; transitive deps are pulled too (no --no-deps) because
        # otherwise pure-Python deps like proxy-tools (transitive of pywebview)
        # never get installed. Binary transitive deps would install host wheels
        # which won't run on Windows — so far we don't have any.
        sdist_cmd = [
            pip_executable, "-m", "pip", "install",
            "--target", str(target_site_packages),
            "--upgrade",
            req,
        ]
        subprocess.run(sdist_cmd, check=True)


def install_windows_wheels(
    requirements_file: Path,
    target_site_packages: Path,
    python_version: str = "311",
    pip_executable: str = sys.executable,
) -> None:
    """Install wheels into target_site_packages for Windows amd64.

    Two-pass strategy: bulk wheels-only install first, per-package fallback
    second if a transitive dep is sdist-only.

    Raises subprocess.CalledProcessError if even the fallback fails on any
    package.
    """
    target_site_packages.mkdir(parents=True, exist_ok=True)
    if _try_only_binary(pip_executable, requirements_file,
                         target_site_packages, python_version):
        return
    print("First-pass --only-binary failed; falling back to per-package install.")
    _fallback_per_package(pip_executable, requirements_file,
                           target_site_packages, python_version)


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
