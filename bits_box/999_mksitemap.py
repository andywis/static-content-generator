#!/usr/bin/env python
"""
This is a "special" component generator. The generated content
will be merged with templates to produce navigation pages.

This is the second of two special component generators. The first one
(000_collect_data.py) collects titles, categories, tags etc and generates
some data-files from the data.
This component generator creates a sitemap and navigation pages from the
data-files.

The numbering of these scripts allows other component generators to modify the
data as needed.

For example, a generated page may wish to append to the list of page 
categories, and have its page appear in the sitemap, or a component generator
could be used to *remove* a page from the sitemap.

N.B. The navigation pages themselves are *not* added to set of pages in the
sitemap.
"""
import json
import os

from awcm import awcm

CONTENT_DIR = '../content'
META_DIR = '../_meta'

SITEMAP_FILE = '000_nav_all_files.html'
CATEGORY_FILE_FMT = '000_nav_%s_%s.html'


def create_sitemap():
    """
    Construct a sitemap of all "real" pages 
    (N.B. doesn't include the generated pages)
    """
    # TODO: read from 000_sitemap.json instead!!
    all_pages = []
    all_content_files = awcm.get_all_filenames(CONTENT_DIR)
    for page in all_content_files:
        if '.html' in page:
            all_pages.append(page)

    sitemap_html = ['<title>Sitemap</title><body><div>',
                    'TODO: Needs to read from 000_sitemap.json instead.!!!',
                    '<ul>']
    for page in all_pages:
        html = awcm.HtmlFileReader(os.path.join(CONTENT_DIR, page))
        page_data = html.read()

        # print(page_data['title'])
        sitemap_html.append('<li><a href="%s">%s</a></li>' % (
            page, page_data['title']))
    sitemap_html.append('</ul></div></body>')

    with open(os.path.join(META_DIR, SITEMAP_FILE), 'w') as fhout:
        fhout.write("\n".join(sitemap_html))


def create_category_pages(data_file, keyword_name):
    """
    Create a set of navigation pages for categories or tags (using
    'category' within this function as a generic name for both.)

    Args:
        data_file: the filename to read (must be JSON)
        keyword_name: one of "Category" or "Tag" saying what
            type of keyword we're talking about.
    """
    if os.path.exists(data_file):
        with open(data_file, 'r') as fh:
            try:
                categories = json.load(fh)
            except ValueError as exc:
                print("  [FAIL] Unable to read %s data %s" % (keyword_name,
                                                              exc))
                categories = None
                exit()

            for kateg, pages in categories.iteritems():
                print("  [info] %s '%s'. pages: %r" % (keyword_name, kateg,
                                                       pages))
                
                title = 'Articles with %s %s' % (keyword_name, kateg)

                # e.g. ../_meta/000_nav_category_misc.html
                # or   ../_meta/000_nav_tag_saxophone.html
                categ_filename = CATEGORY_FILE_FMT % (keyword_name.lower(),
                                                      kateg)
                page_html = [
                    '<meta name="template" content="navigation.thtml />',
                    '<title>%s</title><body>' % title,
                    '<ul>'
                ]
                for page in pages:
                    # TODO: load each page and extract a summary, rather than
                    # just the filename
                    page_html.append('<li><a href="%s">%s</a>' % (page, page))
                page_html.append('<ul>')
                page_html.append('</body>')
                print("  [info] Saving to %s" % categ_filename)
                with open(
                        os.path.join(META_DIR, categ_filename), 'w') as fhout:
                    fhout.write("\n".join(page_html))
    else:
        print("There isn't a %s file" % data_file)


# # TODO: fish the categories out of each page
# #       create a *set* of 000_<categoryname> pages.
# #     - then get the categories injected into the template(s)


create_sitemap()

create_category_pages(
    os.path.join(META_DIR, '000_categories.json'), 
    'Category')

create_category_pages(
    os.path.join(META_DIR, '000_tags.json'), 
    'Tag')
