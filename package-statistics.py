"""
Date: 16 June 2022
Author: Raphael Mercier

Description:
This command line tool takes an architecture as an argument and downloads
the compressed Contents file associated with it from a Debian mirror. It
then prints out the 10 packages that have the most files associated with them.

Usage:
python3 package-statistics.py <arch_name>

"""

import sys
import gzip
from urllib.error import HTTPError
import urllib.request
from collections import Counter

DEBIAN_INDEX_URL = "http://ftp.uk.debian.org/debian/dists/stable/main/"
TOP_PACKAGE_COUNTS_TO_DISPLAY = 10


def get_file_name_from_args() -> str:
    """Return the file name based on the user-provided architecture."""
    try:
        arch_name = sys.argv[1]
        file_name = f"Contents-{arch_name}.gz"
        return file_name
    except IndexError:
        print("You must provide a file name as an argument. Exiting.")
        sys.exit(1)


def download_gzip_file(file_name: str) -> gzip.GzipFile:
    """Download the .gz file and return it as Gzip object."""
    try:
        request = urllib.request.Request(DEBIAN_INDEX_URL + file_name)
        response = urllib.request.urlopen(request)
        gzip_file = gzip.GzipFile(fileobj=response)
        return gzip_file
    except HTTPError:
        print("There is no Contents file associated with the provided architecture. Exiting.")
        sys.exit(1)


def extract_top_packages_by_count(file_string: str) -> Counter:
    """Parse file and return the most commonly used package names and counts as Counter object."""

    # Get the second column, i.e. every second element in the list produced by split().
    packages_col = file_string.split()[1::2]
    # Some elements in the second column are comma separated. Need to split them in place.
    packages_split_by_commas = [x.split(',') for x in packages_col]
    # Since some elements now contain multiple entries, flatten the list.
    flattened_packages = [package for packlist in packages_split_by_commas for package in packlist]

    package_counts = Counter(flattened_packages)
    return package_counts.most_common(TOP_PACKAGE_COUNTS_TO_DISPLAY)


def display_top_packages_by_count(top_packages_by_count: Counter) -> None:
    """Print out the top packages by rank."""
    for i, (name, count) in enumerate(top_packages_by_count):
        print(f"{i + 1 :>3}. {name :<40} {count}")


def main():
    # Infer the file name based on the architecture arg
    file_name = get_file_name_from_args()
    # Download the associated .gz file and make a Gzip object
    gzip_file = download_gzip_file(file_name)
    # Decompress the Gzip object into a string
    decompressed_file_string = gzip_file.read().decode("utf-8")
    # Get the most-used packages as a Counter object
    top_packages_by_count = extract_top_packages_by_count(decompressed_file_string)
    # Display the most-used packages to the user
    display_top_packages_by_count(top_packages_by_count)


if __name__ == "__main__":
    main()
