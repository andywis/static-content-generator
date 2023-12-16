#!/usr/bin/env python

"""
This script adds an empty index.html file to any directory that
does not have an index.html file, to prevent Directory Listings.

As a side effect, it also creates the directory if it doesn't exist.

To use this script
* chmod +x components/998_prevent_directory_listings.py
* make

Minor bug:
  * if an index.html exists in a folder in content/ but not in _meta/, this
    script will create an index.html, but it will be replaced by the output
    of AWCM, with the file from content/
    This should not be an issue.
"""

import json
import os

from awcm import awcm

CONTENT_DIR = "../content"
META_DIR = "../_meta"
THEMES_DIR = "../themes"
OUTPUT_PATH = "../output"

INDEX_HTML_CONTENT = """<br>
"""


def create_index_html_files():
    folder_without_index_file = ['./']

    # Look in both 'content/' nd '_meta/'
    for source_folder in [CONTENT_DIR, META_DIR]:
        all_content_files = awcm.get_all_filenames(source_folder)

        for page in all_content_files:
            if '/' in page:
                folder, file = page.rsplit("/", 1)
                if folder not in folder_without_index_file:
                    if file == 'index.html':
                        pass  # print(f"No need to add an index.html to {folder} ")
                    else:
                        # print(f": Adding index.html to {folder} ")
                        folder_without_index_file.append(folder)

    # Ensure there are index.html files for al the theme folders too
    folder_without_index_file.append(os.path.join(OUTPUT_PATH, 'themes'))
    for theme_name in os.listdir(THEMES_DIR):
        folder_without_index_file.append(os.path.join(OUTPUT_PATH, 'themes', theme_name))

    # iterate all the folders discovered above and create an index.html file in each one.
    for folder in folder_without_index_file:
        new_dir_name = os.path.relpath(os.path.join(OUTPUT_PATH, folder))
        new_file_name = os.path.join(new_dir_name, 'index.html')
        if os.path.isfile(new_file_name):
            print(f"  [INFO] index.html already exists in: {new_dir_name}")
        else:
            print(f"  [INFO] Creating index.html in: {new_dir_name}")
            os.makedirs(new_dir_name, exist_ok=True)
            with open(new_file_name, "w") as f:
                f.write(INDEX_HTML_CONTENT)


create_index_html_files()
