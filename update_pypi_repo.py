import os
import shutil
import sys
import hashlib
import argparse
from urllib.parse import quote


def calculate_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def update_root_index(pkg_name, root_dir):
    """Update the root index.html file with a link to the package."""
    index_file = os.path.join(root_dir, "index.html")
    link_entry = f'<a href="{pkg_name}" rel="internal">{pkg_name}</a>'

    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        if link_entry not in content:
            content = content.replace("</body>", f"{link_entry}\n</body>")
    else:
        content = f'<!DOCTYPE html>\n<html><head><title>Simple Index</title><meta name="api-version" value="2" /></head><body>\n{link_entry}\n</body></html>'

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(content)


def update_package_index(pkg_name, version, whl_file, root_dir, base_url):
    """Update the index.html file in the package directory with the new .whl file."""
    package_dir = os.path.join(root_dir, pkg_name)
    index_file = os.path.join(package_dir, "index.html")
    sha256_hash = calculate_sha256(whl_file)
    whl_filename = os.path.basename(whl_file)
    whl_url = f"{base_url}/{pkg_name}/{version}/{quote(whl_filename)}#sha256={sha256_hash}"
    link_entry = f'        <a href="{whl_url}" data-requires-python="&gt;=3.8, &lt;3.13" rel="internal">{whl_filename}</a>'

    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        if link_entry not in content:
            content = content.replace("</body>", f"{link_entry}\n    </body>")
    else:
        content = f'<!DOCTYPE html>\n<html>\n    <head>\n        <title>Simple Index</title>\n        <meta name="api-version" value="2"/>\n    </head>\n    <body>\n{link_entry}\n    </body>\n</html>'

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(content)


def process_whl_file(whl_file, root_dir, base_url):
    """Process a .whl file and update the directory structure and index.html files."""
    if not os.path.exists(whl_file):
        print(f"Error: File {whl_file} does not exist.")
        return

    whl_filename = os.path.basename(whl_file)
    parts = whl_filename.split("-")
    if len(parts) < 2:
        print(f"Error: Invalid .whl filename format: {whl_filename}")
        return

    pkg_name = parts[0]
    version = parts[1]

    pkg_version_dir = os.path.join(root_dir, pkg_name, version)
    os.makedirs(pkg_version_dir, exist_ok=True)

    dest_whl_path = os.path.join(pkg_version_dir, whl_filename)
    shutil.copy2(whl_file, dest_whl_path)

    update_root_index(pkg_name, root_dir)
    update_package_index(pkg_name, version, dest_whl_path, root_dir, base_url)
    print(f"Successfully processed {whl_file} and updated index files.")


def main():
    parser = argparse.ArgumentParser(
        description="Process a .whl file and update the directory structure and index.html files.")
    parser.add_argument("--whl_file", help="Path to the .whl file")
    parser.add_argument("--root_dir", default=".", help="Root directory for storing package files")
    parser.add_argument("--base_url", help="Base URL for the package repository")

    args = parser.parse_args()
    process_whl_file(args.whl_file, args.root_dir, args.base_url)


if __name__ == "__main__":
    main()
