"""Package Linux build for distribution."""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def package_linux():
    """Create tar.gz archive of Linux build."""

    build_dir = PROJECT_ROOT / "dist" / "audiobook-reader-gui"

    if not build_dir.exists():
        print(f"❌ ERROR: Build directory not found: {build_dir}")
        print("   Run build_linux.py first")
        sys.exit(1)

    print(f"✓ Found build directory: {build_dir}")

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

    # Create tar.gz archive
    archive_name = f"audiobook-reader-gui-{version}-Linux"
    archive_path = PROJECT_ROOT / "dist" / archive_name

    print(f"Creating tar.gz archive: {archive_name}.tar.gz")

    shutil.make_archive(
        str(archive_path),
        'gztar',
        PROJECT_ROOT / "dist",
        "audiobook-reader-gui"
    )

    archive_file = Path(f"{archive_path}.tar.gz")
    size_mb = archive_file.stat().st_size / (1024 * 1024)

    print(f"\n✓ Package created: {archive_file}")
    print(f"  Size: {size_mb:.1f} MB")
    print("\nReady for distribution!")
    print("\nTo install on Linux:")
    print("  1. Extract: tar -xzf audiobook-reader-gui-*.tar.gz")
    print("  2. Run: ./audiobook-reader-gui/audiobook-reader-gui")

if __name__ == "__main__":
    package_linux()
