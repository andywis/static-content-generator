#!/usr/bin/env python

# An attempt at writing a content generator
# loads all filenames and prints out some of the content.
# Don't forget to "chmod +x <filename>"

# TODO: Pagination?


import json
import os
import re

from awcm import awcm

CONTENT_DIR = '../content'
META_DIR = '../_meta'
SITEMAP_DATA_FILE = os.path.join(META_DIR, '000_sitemap.json')
CATEGORY_DATA_FILE = os.path.join(META_DIR, '000_categories.json')
TAG_DATA_FILE = os.path.join(META_DIR, '000_tags.json')

OUTFILE = os.path.join(META_DIR, 'index.html')

# Max size of previews. "Max Preview Length" is the trigger size
# truncate_at is the size after truncating. By having a difference
# between these two, we never see a file with only the final word
# truncated.
MAX_PREVIEW_LENGTH = 2700
TRUNCATE_AT = 2400

def main():
    all_content_files = awcm.get_all_filenames(CONTENT_DIR)

    output = ['<title>Home</title>']

    # Ensure they're in the right order
    all_content_files.sort(reverse=True)

    for page_filename in all_content_files:
        # Ignore non-HTML files
        if '.html' not in page_filename:
            continue

        # Ignore filenames that don't match a pattern
        if not re.match('\d.*\.html', page_filename):
            continue

        reader = awcm.HtmlFileReader(os.path.join(CONTENT_DIR, page_filename))
        page_content = reader.read()
        title = page_content['title']
        full_content = awcm.fix_incomplete_html(page_content['content'])

        is_truncated = False
        if len(full_content) > MAX_PREVIEW_LENGTH:
            content = awcm.fix_incomplete_html(full_content[0:TRUNCATE_AT])
            is_truncated = True
            opener_link_text = "more... ({} bytes)".format(len(full_content))
        else:
            content = full_content
            opener_link_text = "open..."

        content = awcm.html_encode(content)

        output.append("<h2><a href=\"{0}\">{1}</a></h2>".format(page_filename,
                                                                title))
        output.append("<div>")
        output.append(content)
        output.append("<div style=\"padding-bottom:20px\">")
        output.append("<a href=\"{0}\">{1}</a></h2>".format(page_filename,
                                                            opener_link_text))
        output.append("</div></div>")

    with open (OUTFILE, 'w') as fhout:
        fhout.write(''.join(output))

main()
