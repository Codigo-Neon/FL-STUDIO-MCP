"""Download Python 3.11 embedded distribution from python.org and prepare it
for use as the bundled interpreter inside the installer.

The embedded distribution is a self-contained Python: a single directory
containing python.exe, python311.dll, the standard library zipped, and a
`._pth` file that controls sys.path. By default the `_pth` excludes
site-packages; we patch it to include site-packages so pip-installed wheels
work.
"""
import io
import urllib.request
import zipfile
from pathlib import Path

PYTHON_VERSION = "3.11.9"


def embed_zip_url(version: str = PYTHON_VERSION) -> str:
    """Return the official python.org download URL for the embedded amd64 ZIP."""
    return (
        f"https://www.python.org/ftp/python/{version}/"
        f"python-{version}-embed-amd64.zip"
    )


def patch_pth_to_enable_site(pth_path: Path) -> None:
    """Uncomment the `#import site` line in the embedded `_pth` file.

    Without this, `Lib/site-packages` is not on sys.path and pip-installed
    wheels are invisible. With it, the embedded interpreter behaves like a
    normal install for our purposes.
    """
    text = pth_path.read_text()
    text = text.replace("#import site", "import site")
    pth_path.write_text(text)


def fetch_and_extract(
    target_dir: Path,
    version: str = PYTHON_VERSION,
) -> Path:
    """Download + extract the embedded Python distribution into `target_dir`.

    Patches the `_pth` file before returning. Returns `target_dir`.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    url = embed_zip_url(version)
    with urllib.request.urlopen(url, timeout=120) as response:
        zip_bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(target_dir)

    # Find and patch the _pth file (name varies by minor version: python311._pth,
    # python312._pth, etc.)
    for pth in target_dir.glob("python*._pth"):
        patch_pth_to_enable_site(pth)

    return target_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download Python embedded distribution.")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--version", type=str, default=PYTHON_VERSION)
    args = parser.parse_args()
    result = fetch_and_extract(target_dir=args.target, version=args.version)
    print(f"Python {args.version} embedded extracted to {result}")
