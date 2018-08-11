#!/usr/bin/env python


"""
What is this?
    AWCM (Andy's Web Content Manager, pronounced "Awesome", which is a very
    ostentatious name for what it is) is a Static site generator influenced
    by Jekyll and Pelican.

    I had a go at using Pelican to create web pages; It's generally great,
    but didn't quite meet my needs.
    Some of the things I wanted to do were:
        - Ability to customise the theme on a per-page basis.
        - A *page* for the homepage
        - Page names based on filenames, not slugs.
        - Jinja2 and BeautifulSoup :-)
"""

import json
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup
import jinja2

CONFIG_FILE_NAME = 'config.json'

CONFIG = {
    'theme': '_not_set_',  # Should be specified in config.json
    'default_template': 'common.thtml',
    'content_dir': './content',
    'themes_root': './themes',
    'output_path': './output',
    'debug': True,
}


def read_site_config(relative_dir=None):

    # Start looking in the current directory for the config file. If
    # relative_dir is set, use this to adjust the path.

    # look in current dir, and if current dir == 'components', go up a level.
    # if there's one in components AND the main dir, we load the nearest one.
    if relative_dir:
        cfg_location = os.path.join(os.getcwd(), relative_dir,
                                    CONFIG_FILE_NAME)
    else:
        cfg_location = os.path.join(os.getcwd(), CONFIG_FILE_NAME)

    if os.path.exists(cfg_location):
        with open(cfg_location, 'r') as jsonfh:
            local_config = json.load(jsonfh)
    else:
        # TODO: tidy this up with a custom exception
        raise Exception('No config file')

    # Mandatory config parameters
    CONFIG['theme'] = local_config['theme']

    # Optional config parameters
    if 'default_template' in local_config.keys():
        CONFIG['default_template'] = local_config['default_template']


def html_encode(text):
    """ Encode the text for web pages; convert anything
    that's non-ASCII into its XML/HTML representation.

    text must be a unicode string
    """
    try:
        return text.encode('ascii', 'xmlcharrefreplace')

    except UnicodeDecodeError as exc:
        print("*" * 30)
        print("Unicode error encountered")
        mtch = re.search('in position (\d+):', str(exc))
        posn = int(mtch.group(1))
        portion = text[posn-30:posn]
        portion = re.sub("[\n\r]+", ' [NL] ', portion)
        print("Chars leading up to position %d: ...%s" % (
            posn, portion))
        print("Chars around position %d: ...%s..." % (
            posn, text[posn-3:posn+6]))
        print("*" * 30)
        raise


def mkdir_p(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_all_filenames(root_dir):
    file_list = []
    for root, _directories, filenames in os.walk(root_dir):
        for filename in filenames:
            filename = re.sub(root_dir + '/', '', os.path.join(root, filename))
            if not re.match(r"/\.git/", filename):
                file_list.append(filename)
    return file_list


def copy_static_files(templates_dir, theme_name, output_dir):
    """ Copy the static files for the specified theme """
    source_dir = os.path.join(templates_dir, theme_name, 'static')
    destination = output_dir
    for filename in os.listdir(source_dir):
        print("Copy %s" % filename)
        if os.path.isfile(os.path.join(source_dir, filename)):
            print('copying file')
            shutil.copy(os.path.join(source_dir, filename),
                        destination)
        # We don't currently copy folders. If we did, shutil.copytree
        # would be the tool to use.


def get_back_path(path_to_file):
    """ calculate the back-path to get back to the root folder from
    a specific file
    path_to_file is the path to a specified file.
    Returns the "../../" string to get back to the top level.
    """
    path_to_file = path_to_file.replace('//', '/')
    # remove leading './'
    if path_to_file[0:2] == './':
        path_to_file = path_to_file[2:]

    num_dirs = path_to_file.count('/')
    return '../' * num_dirs


def fix_incomplete_html(in_html):
    """
    Fix a block of HTML by adding the missing (closing) tags.
    returns: a string of HTML equivalent to the input, but with the
    correct closing tags

    This is accomplished by reading the HTML into Beautifulsoup.
    'lxml' and 'html5lib' give slightly different results when
    processing an incomplete tag at the end of the abbreviated
    document.

    N.B. in an earlier implementation, I tried using .prettify() but this
    doesn't add anything useful, and modifies whitespace.
    """

    soup = BeautifulSoup(in_html, 'lxml')
    if sys.version_info[0] < 3:
        soup_str = unicode(soup)
    else:
        soup_str = str(soup)
    # fish out the the bit INSIDE the <body> tag
    inner_body = re.sub('.*<body>\s*(.*)</body>.*',
                        r'\1', soup_str, flags=re.S)

    return inner_body


class HtmlFileReader:
    def __init__(self, filename):
        """ filename is the full relative path to the file
        and probably contains at least one '/' character.
        """
        self.filename = filename

    def load(self):
        """ Load the HTML from file into memory """
        full_path = self.filename
        with open(full_path, 'r') as content_fh:
            raw_html = content_fh.read()
        return raw_html

    def read(self):
        raw_html = self.load()
        return self.parse_html(raw_html)

    def _get_title(self, soup):
        """ Given a 'Soup' Object, find the title."""
        titles = soup.find_all('title')
        if titles:
            # See https://stackoverflow.com/a/18602241
            # decode_contents() may be undocumented.
            title = html_encode(unicode(titles[0].decode_contents(
                formatter="html")))
        else:
            title = '[[NO TITLE FOUND]]'
        return title

    def _get_content(self, soup):
        """ Given a 'Soup' Object, find the page content"""
        page_body = soup.find('body')
        if page_body is not None and page_body.find_next():
            page_content = html_encode(unicode(page_body.decode_contents(
                formatter="html")))
        else:
            page_content = '[[YOUR CONTENT SHOULD GO HERE]]'
        return page_content

    def _get_meta_data(self, soup):
        """ Given a 'Soup' Object, find the page meta-data"""
        meta_data = {}
        all_meta_tags = soup.find_all('meta')
        meta_data['_raw_metas'] = all_meta_tags
        # Valid meta-tags are based on the tags supported by Pelican, with a
        # few extra ones that I consider useful (e.g. a page can be in
        # multiple categories)
        # See http://docs.getpelican.com/en/3.6.3/content.html#file-metadata
        valid_metatag_names = ['authors', 'categories', 'category', 'date',
                               'modified', 'summary', 'tags', 'theme',
                               'template']
        for meta_tag in all_meta_tags:
            # e.g <meta name="category" content="misc" />
            for attr in valid_metatag_names:
                if 'name' in meta_tag.attrs.keys():
                    if (meta_tag['name'] == attr and
                            'content' in meta_tag.attrs.keys()):

                        # Special case: merge category and categories
                        if attr == 'category':
                            attr = 'categories'

                        # Create a blank if it doesn't exist
                        if attr not in meta_data.keys():
                            meta_data[attr] = meta_tag['content']
                        else:
                            meta_data[attr] += ', ' + meta_tag['content']
        return meta_data

    def parse_html(self, html_in):
        """ Parse an HTML string and extract certain components/elements """
        soup = BeautifulSoup(html_in, 'lxml')

        title = self._get_title(soup)
        page_content = self._get_content(soup)
        meta_data = self._get_meta_data(soup)
        meta_data['title'] = title
        return {'content': page_content, 'title': title, 'meta': meta_data}


class TemplateWriter:
    def __init__(self, templates_dir):
        template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
        self.template_env = jinja2.Environment(loader=template_loader)
        self._templates_dir = templates_dir

    def read(self, template_file):
        """ Read a template file.
        template_file is the full path to the template"""
        tmpl = self.template_env.get_template(template_file)
        return tmpl

    def write(self, output_dir, output_file_path, theme_name, template_name,
              tokens):
        """ Write a file using the specified template

        Args:
            output_dir: folder to contain all the generated files
            output_file_path: full relative path to the file being saved
            theme_name: name of the theme
            template_name: name of the template
            tokens: Template tokens
        """

        if template_name[-6:] != '.thtml':
            template_name = template_name + '.thtml'

        try:
            template = self.read(os.path.join(theme_name,
                                              'templates',
                                              template_name))
        except jinja2.exceptions.TemplateNotFound as exc:
            # str(exc) gives us the path to the missing template
            print("\nERROR: Could not read template file: %s\n" %
                  os.path.join(self._templates_dir, str(exc)))
            print("Terminating")
            sys.exit()

        tokens['back_path'] = get_back_path(output_file_path)
        tokens['theme_path'] = tokens['back_path'] + 'themes/' + \
            theme_name + '/'
        full_save_path = os.path.join(output_dir, output_file_path)

        with open(full_save_path, 'w') as output_fh:
            output_fh.write(template.render(tokens))

    def validate_template(self, theme_name):
        expected_files = [
            'templates/common.thtml',
            'templates/navigation.thtml',
        ]
        passed = True
        for f in expected_files:
            full_path = os.path.join(self._templates_dir, theme_name, f)
            if not os.path.exists(full_path):
                print("\n/!\\  WARNING: Expected template file missing: %s\n" %
                      full_path)
                passed = False
        return passed


def get_tag_list_as_html(back_path=''):
    """
    Generate a <UL> list of tags to be injected into the template
    """
    tags_file = os.path.join('_meta', '000_tags.json')
    nav_page_fmt = back_path + '000_nav_tag_%s.html'
    return get_tag_or_category_as_html(tags_file, nav_page_fmt,
                                       'awcm-tag')


def get_category_list_as_html(back_path=''):
    """
    Generate a <UL> list of categories to be injected into the template
    """
    categories_file = os.path.join('_meta', '000_categories.json')
    nav_page_fmt = back_path + '000_nav_category_%s.html'
    return get_tag_or_category_as_html(categories_file, nav_page_fmt,
                                       'awcm-category')


def get_tag_or_category_as_html(data_file, nav_page_fmt, css_class):
    """ Does both Tags and Categories, as the logic is identical """
    if os.path.exists(data_file):
        with open(data_file) as data_fh:
            all_tags = json.load(data_fh)
            html = ['<ul class="{}">'.format(css_class)]
            for tag in all_tags.keys():
                url = nav_page_fmt % tag
                html.append('<li><a href="%s">%s</a>&nbsp;(%d)</li> ' %
                            (url, tag, len(all_tags[tag])))
            html.append('</ul>')
            # print(html)
            return ''.join(html)
    return ''
    

def get_template_name(article_data):
    """
    Get the template from the config or from the metadata in
    the article.

    :param article_data: Data as returned by HtmlFileReader;
        can be an empty dict.
    :return: the template name
    """
    template = CONFIG['default_template']

    if 'meta' in article_data.keys():
        if 'template' in article_data['meta'].keys():
            print("  custom template: " + article_data['meta']['template'])
            template = article_data['meta']['template']

    return template


def get_theme_name(article_data):
    """
    Get the theme name from either the config or the metadata in
    the article
    :param article_data:
    :return: the theme name
    """
    theme = CONFIG['theme']

    if 'meta' in article_data.keys():

        if 'theme' in article_data['meta'].keys():
            print("  custom theme: " + article_data['meta']['theme'])
            theme = article_data['meta']['theme']
    return theme


def make_pages_from_template(templates_dir, output_dir):
    t = TemplateWriter(templates_dir)

    for input_source in [CONFIG['content_dir'], '_meta']:
        for file_path in get_all_filenames(input_source):
            if file_path.split('.')[-1] in ['html', 'htm']:
               
                if CONFIG['debug']:
                    print("Writing %s from %s" % (file_path, input_source))

                article_data = HtmlFileReader(
                    os.path.join(input_source, file_path)).read()

                template = get_template_name(article_data)
                theme_name = get_theme_name(article_data)

                t.validate_template(theme_name)

                back_path = get_back_path(file_path)
                tokens = {'title': article_data['title'],
                          'article': article_data['content'],
                          'tags_html': get_tag_list_as_html(
                              back_path=back_path),
                          'categories_html': get_category_list_as_html(
                              back_path=back_path),
                          }

                # everything about a page:
                #   - file_path (source file)
                #   - theme_name (from config, could be overridden in
                #                 the metadata)
                #   - article_data
                #   - template (name of the template to use)
                #   - output_file_path (currently same as source path; could be
                #           overridden in metadata)

                full_output_path = os.path.join(output_dir, file_path)

                # Make the folder
                full_output_dir = os.path.dirname(full_output_path)
                if not os.path.exists(full_output_dir):
                    os.makedirs(full_output_dir)

                t.write(output_dir=output_dir,
                        output_file_path=file_path,
                        theme_name=theme_name,
                        template_name=template,
                        tokens=tokens)
                # TODO: Collect the theme names as we go.

            elif input_source == '_meta' and\
                    file_path.split('.')[-1] in ['json', 'yml', 'yaml']:
                # Ignore data files in _meta/
                pass
            else:
                if CONFIG['debug']:
                    print("Not Templatising %s" % file_path)
                # Just copy the file unmodified.
                shutil.copy(os.path.join(input_source, file_path),
                            os.path.join(output_dir, file_path))
        

def main():
    read_site_config()
    # Ensure _meta and output folders exist
    mkdir_p(CONFIG['output_path'])
    mkdir_p('_meta')
    mkdir_p(os.path.join(CONFIG['output_path'], 'themes'))

    make_pages_from_template(templates_dir=CONFIG['themes_root'],
                             output_dir=CONFIG['output_path'])

    theme = CONFIG['theme']
    theme_static_dir = os.path.join(CONFIG['output_path'], 'themes', theme)
    mkdir_p(theme_static_dir)

    copy_static_files(templates_dir=CONFIG['themes_root'], theme_name=theme,
                      output_dir=theme_static_dir)


if __name__ == '__main__':
    main()
