import os
import shutil
import sys
import zipfile
from pathlib import Path
from packaging.utils import canonicalize_name
from packaging.version import parse

# Define repo root folder
REPO_ROOT = Path(__file__).parent

def extract_metadata(whl_path):
    """Extracts package name and version from a .whl filename."""
    whl_name = Path(whl_path).stem  # Remove .whl extension
    parts = whl_name.split('-')  # whl filename format: pkgname-version-python-arch.whl

    if len(parts) < 2:
        raise ValueError(f"Invalid .whl filename format: {whl_name}")

    pkg_name = canonicalize_name(parts[0])  # Normalize name (e.g., PyYAML -> pyyaml)
    version = parts[1]
    return pkg_name, version

def create_package_structure(whl_path, repo_root):
    """Creates the folder structure and copies the .whl file."""
    pkg_name, version = extract_metadata(whl_path)
    pkg_folder = repo_root / "files" / pkg_name / version
    pkg_folder.mkdir(parents=True, exist_ok=True)

    # Copy .whl file
    dest_whl_path = pkg_folder / Path(whl_path).name
    shutil.copy2(whl_path, dest_whl_path)

    # Update HTML index
    update_package_index(pkg_name, repo_root)

def update_package_index(pkg_name, repo_root):
    """Updates or creates the package index file."""
    pkg_folder = repo_root / "files" / pkg_name
    html_path = repo_root / f"{pkg_name}.html"

    links = []
    for version_folder in sorted(pkg_folder.iterdir(), key=lambda p: parse(p.name)):
        for whl_file in version_folder.glob("*.whl"):
            rel_path = os.path.relpath(whl_file, repo_root)
            links.append(f'<a href="{rel_path}" rel="internal">{whl_file.name}</a>')

    html_content = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "    <head>\n"
            "        <title>Simple Index</title>\n"
            "        <meta name=\"api-version\" value=\"2\"/>\n"
            "    </head>\n"
            "    <body>\n"
            "        " + "\n        ".join(links) + "\n"
                                                    "    </body>\n"
                                                    "</html>\n"
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_pypi_repo.py <path_to_whl>")
        sys.exit(1)

    whl_path = Path(sys.argv[1])
    if not whl_path.exists() or not whl_path.suffix == ".whl":
        print(f"Invalid .whl file: {whl_path}")
        sys.exit(1)

    create_package_structure(whl_path, REPO_ROOT)
    print(f"Package {whl_path.name} added to the repository.")
