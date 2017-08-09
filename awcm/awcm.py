#!/usr/bin/env python


"""
What is this?
    AWCM (the AndyWis Content Manager, pronounced "Awesome", but that's
    rather grandiose and arrogant!) is a Static site generator infuenced
    by Jekyll and Pelican.

    I had a go at using Pelican to create web pages; It's generally great,
    but didn't quite meet my needs.
    See ~/Documents/www/notes.txt on Macbook
        - Ability to customise the theme on a per-page basis.
        - A *page* for the homepage
        - Page names based on filenames, not slugs.
        - Jinja2 and BeautifulSoup :-)

TODO:
    - *** See index.html for the to do list ***


"""

import os
import re
import shutil
import subprocess

from bs4 import BeautifulSoup
import jinja2

CONFIG = {
    'theme': 'balquidhur',
    # 'default_template': 'page.thtml',
    'start_page_template': 'common.thtml',
    'content_dir': './content',
    'templates_dir': './templates',
    'output_path': './output',
    'debug': False,
}


def html_encode(text):
    """ Encode the text for web pages; convert anything
    that's non-ASCII into its XML/HTML representation."""
    return text.encode('ascii', 'xmlcharrefreplace')


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
    for file in os.listdir(source_dir):
        print("Copy %s" % file)
        if os.path.isfile(os.path.join(source_dir, file)):
            print('copying file')
            shutil.copy(os.path.join(source_dir, file),
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
    return ('../' * num_dirs)


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

    def parse_html(self, html_in):
        """ Parse an HTML string and extract certain components/elements """
        soup = BeautifulSoup(html_in, 'lxml')

        titles = soup.find_all('title')
        if titles:
            # See https://stackoverflow.com/a/18602241
            # decode_contents() may be undocumented.
            title = html_encode(unicode(titles[0].decode_contents(
                formatter="html")))
        else:
            title = '[[NO TITLE FOUND]]'

        page_body = soup.find('body')
        if page_body.find_next():
            page_content = html_encode(unicode(page_body.decode_contents(
                formatter="html")))
        else:
            page_content = '[[YOUR CONTENT SHOULD GO HERE]]'

        meta_data = {'title': title}

        meta_data['_raw_metas'] = soup.find_all('meta')

        return {'content': page_content, 'title': title, 'meta': meta_data}

    def find_metadata(self, html_in):
        """ Find meta-data inside ... """
        pass

class TemplateWriter:
    def __init__(self, templates_dir):
        template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
        self.template_env = jinja2.Environment(loader=template_loader)

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
        """
        template = self.read(os.path.join(theme_name,
                                          'templates',
                                          template_name))

        tokens['back_path'] = get_back_path(output_file_path)
        full_save_path = os.path.join(output_dir, output_file_path)

        with open(full_save_path, 'w') as output_fh:
            output_fh.write(template.render(tokens))


def make_pages_from_template(templates_dir, output_dir):
    t = TemplateWriter(templates_dir)

    for input_source in [CONFIG['content_dir'], '_meta']:

        for file_path in get_all_filenames(input_source):

            if CONFIG['debug']:
                print("Writing %s from %s" % (file_path, input_source))
            theme_name = CONFIG['theme']
            template = CONFIG['start_page_template']

            article_data = HtmlFileReader(
                os.path.join(input_source, file_path)).read()

            tokens = {'title': article_data['title'],
                      'article': article_data['content']}

            # everything about a page:
            #   - file_path (source file)
            #   - theme_name (from config, could be overridden in the metadata)
            #   - article_data
            #   - template (name of the template to use)
            #   - output_file_path (currently same as source path; could be
            #           overridden in metadata)

            full_output_path = os.path.join(output_dir, file_path)
            print("writing to %s" % full_output_path)

            t.write(output_dir=output_dir,
                    output_file_path=file_path,
                    theme_name=theme_name,
                    template_name=template,
                    tokens=tokens)

        # TODO: Collect the theme names as we go.


def main():
    # Ensure _meta and output folders exist
    mkdir_p(CONFIG['output_path'])
    mkdir_p('_meta')
    mkdir_p(os.path.join(CONFIG['output_path'], 'th'))

    make_pages_from_template(templates_dir=CONFIG['templates_dir'],
                             output_dir=CONFIG['output_path'])

    theme = CONFIG['theme']
    theme_static_dir = os.path.join(CONFIG['output_path'], 'th', theme)
    mkdir_p(theme_static_dir)

    copy_static_files(templates_dir=CONFIG['templates_dir'], theme_name=theme,
                      output_dir=theme_static_dir)


if __name__ == '__main__':
    main()
