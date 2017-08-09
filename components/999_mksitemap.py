#!/usr/bin/env python
"""
This is a "special" component generator. The generated content
is injected into templates. (or at least, it _will_ be!!)

There are two "special" component generators: 000_collect_data.py and 999_mksitemap.py
The first one collects page titles and categories from data in the "content/" folder
and creates some data files.
The second one creates the sitemap from these data files. 
The numbering of these scripts allows other component generators to modify the data
as needed.

For example, a generated page may wish to append to the list of page categories, and
have its page appear in the sitemap, or a component generator could be used to *remove*
a page from the sitemap.
"""
import os

from awcm import awcm

CONTENT_DIR = '../content'
META_DIR = '../_meta'

def create_sitemap():
    """
    Construct a sitemap of all "real" pages 
    (N.B. doesn't include the generated pages)
    """
    all_pages = []
    all_content_files = awcm.get_all_filenames(CONTENT_DIR)
    for page in all_content_files:
        if '.html' in page:
            all_pages.append(page)

    sitemap_html = ['<title>Sitemap</title><body><div><ul>']
    for page in all_pages:
        html = awcm.HtmlFileReader(os.path.join(CONTENT_DIR, page))
        page_data = html.read()

        print(page_data['title'])
        sitemap_html.append('<li><a href="%s">%s</a></li>' % (page, page_data['title']))

    sitemap_html.append('</ul></div></body>')

    with open(os.path.join(META_DIR, '000_all_files.html'), 'w') as fhout:
        fhout.write("\n".join(sitemap_html))


# # TODO: fish the categories out of each page
# #       (may need to be done in Python)
# #       create a *set* of 000_<categoryname> pages.
# #     - then get the categories injected into the template(s)
# exit

create_sitemap()
