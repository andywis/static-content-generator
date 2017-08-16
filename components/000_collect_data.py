#!/usr/bin/env python
"""
This is a "special" component generator. The generated content
is injected into templates. (or at least, it _will_ be!!)

There are two "special" component generators: 000_collect_data.py and
999_mksitemap.py.
The first one collects page titles, categories and tags from data in the
"content/" folder and creates some data files.
The second one creates the sitemap and navigation pages from these data files.
The numbering of these scripts allows other component generators to modify the
data as needed.

For example, a generated page may wish to append to the list of page
categories, and have its page appear in the sitemap, or a component generator
could be used to *remove* a page from the sitemap.
"""
import json
import os

from awcm import awcm

CONTENT_DIR = '../content'
META_DIR = '../_meta'
SITEMAP_DATA_FILE = os.path.join(META_DIR, '000_sitemap.json')
CATEGORY_DATA_FILE = os.path.join(META_DIR, '000_categories.json')
TAG_DATA_FILE = os.path.join(META_DIR, '000_tags.json')

VERBOSE = True


def collect_data():
    """
    Collect page titles and save them to SITEMAP_DATA_FILE so that a sitemap
    can be built by 999_mksitemap.py

    Collect category data from <meta> tags and save them to CATEGORY_DATA_FILE
    so that cagetories can be added to pages (via templates) and category pages
    can be constructed.
    """
    all_content_files = awcm.get_all_filenames(CONTENT_DIR)

    sitemap_entries = []
    categories = {}
    tags = {}
    for page in all_content_files:
        # Ignore non-HTML files
        if '.html' not in page:
            continue

        html = awcm.HtmlFileReader(os.path.join(CONTENT_DIR, page))
        page_data = html.read()

        if VERBOSE:
            print('  [info] Title of %s is %s' % (page, page_data['title']))

        sitemap_entries.append({'title': page_data['title'], 'url': page})

        # categories and tags (both can be comma separated lists) meta data as
        # per http://docs.getpelican.com/en/3.6.3/content.html#file-metadata
        if 'categories' in page_data['meta'].keys():
            if VERBOSE:
                print("  [info] Page %s has categories: %s" % (
                    page, page_data['meta']['categories']))

            for category in page_data['meta']['categories'].split(','):
                if category in categories.keys():
                    categories[cagetory].append(page)
                else:
                    categories[category] = [page] 

        if 'tags' in page_data['meta'].keys():
            if VERBOSE:
                print("  [info] Page %s has tags: %s" % (
                    page, page_data['meta']['tags']))
            for tag in page_data['meta']['tags'].split(','):
                if tag in tags.keys():
                    tags[tag].append(page)
                else:
                    tags[tag] = [page]

    with open(SITEMAP_DATA_FILE, 'w') as fhout:
        json.dump(sitemap_entries, fhout)

    with open(CATEGORY_DATA_FILE, 'w') as fhout:
        json.dump(categories, fhout)

    with open(TAG_DATA_FILE, 'w') as fhout:
        json.dump(tags, fhout)


collect_data()
