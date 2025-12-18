"""Package Windows build for distribution."""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def package_windows():
    """Create ZIP archive of Windows build."""

    build_dir = PROJECT_ROOT / "dist" / "AudiobookReader"

    if not build_dir.exists():
        print(f"ERROR: Build directory not found: {build_dir}")
        print("   Run build_windows.py first")
        sys.exit(1)

    print(f"Found build directory: {build_dir}")

    # Get version from pyproject.toml
    try:
        # Read version without needing toml library
        with open(PROJECT_ROOT / "pyproject.toml", 'r') as f:
            for line in f:
                if line.startswith('version = '):
                    version = line.split('"')[1]
                    break
            else:
                version = "unknown"
    except:
        version = "unknown"

    # Create ZIP archive
    zip_name = f"AudiobookReader-{version}-Windows"
    zip_path = PROJECT_ROOT / "dist" / zip_name

    print(f"Creating ZIP archive: {zip_name}.zip")

    shutil.make_archive(
        str(zip_path),
        'zip',
        PROJECT_ROOT / "dist",
        "AudiobookReader"
    )

    zip_file = Path(f"{zip_path}.zip")
    size_mb = zip_file.stat().st_size / (1024 * 1024)

    print(f"\nPackage created: {zip_file}")
    print(f"  Size: {size_mb:.1f} MB")
    print("\nReady for distribution!")

if __name__ == "__main__":
    package_windows()
