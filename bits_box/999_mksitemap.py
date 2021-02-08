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

# ----------
#        Duplicated from 001_make_homepage
# Max size of previews. "Max Preview Length" is the trigger size
# truncate_at is the size after truncating. By having a difference
# between these two, we never see a file with only the final word
# truncated.
MAX_PREVIEW_LENGTH = 1500
TRUNCATE_AT = 1200


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


def get_page_summary(page, max_preview_length, truncate_at):
    """
    Creates a summary of a page (truncated according to the truncation
    parameters.)

    Args:
        page: the relative path to the page

    TODO: Move this method to awcm utils

    Returns a list of HTML portions which are inteneded to be added
    to an existing list (which will be joined before rendering)
    """
    html_bits = []
    reader = awcm.HtmlFileReader(os.path.join(CONTENT_DIR, page))
    page_content = reader.read()
    article_title = page_content['title']
    full_content = awcm.fix_incomplete_html(page_content['content'])

    is_truncated = False
    if len(full_content) > max_preview_length:
        content = awcm.fix_incomplete_html(full_content[0:truncate_at])
        is_truncated = True
        opener_link_text = "more... ({} bytes)".format(len(full_content))
    else:
        content = full_content
        opener_link_text = "open..."

    html_bits.append("<h2><a href=\"{0}\">{1}</a></h2>".format(
        page, article_title))
    html_bits.append("<div>")
    html_bits.append(content)
    # html_bits.append(awcm.html_encode(content).decode('UTF-8'))
    html_bits.append("<div style=\"padding-bottom:20px\">")
    html_bits.append("<a href=\"{0}\">{1}</a></h2>".format(
        page, opener_link_text))
    html_bits.append("</div></div><div style=\"clear:both;\"></div><hr/>")

    return html_bits


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

            for kateg, pages in categories.items():
                print("  [info] %s '%s'. pages: %r" % (keyword_name, kateg,
                                                       pages))
                
                title = 'Articles with %s %s' % (keyword_name, kateg)

                # e.g. ../_meta/000_nav_category_misc.html
                # or   ../_meta/000_nav_tag_saxophone.html
                categ_filename = CATEGORY_FILE_FMT % (keyword_name.lower(),
                                                      kateg)
                page_html = [
                    '<meta name="template" content="navigation.thtml" />',
                    '<title>%s</title><body>' % title,
                ]
                for page in pages:
                    # N.B. duplicated from 001_make_homepage
                    page_html = page_html + get_page_summary(
                        page, MAX_PREVIEW_LENGTH, TRUNCATE_AT)
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
