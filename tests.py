#!/usr/bin/env python
# coding: utf-8
# Tests for AWCM (run with pytest ./tests.py)

import os
import random
import shutil
import string
import tempfile

import pytest

from awcm.awcm import get_back_path, HtmlFileReader, \
    get_template_name, get_theme_name, html_encode, \
    fix_incomplete_html, mkdir_p, read_site_config, \
    CONFIG, TemplateWriter


def test_read_content():
    hfr = HtmlFileReader('no_filename')

    html_frag = """
    <head>
      <title>Gandalf</title>
      <body>
        <p>Bilbo Baggins</p>
        <p>Bard the Bowman</p>
        <p>Thorin Oakenshield</p>
      </body>
    """
    parts = hfr.parse_html(html_frag)

    expected = '''
<p>Bilbo Baggins</p>
<p>Bard the Bowman</p>
<p>Thorin Oakenshield</p>
'''
    assert parts['content'] == expected


def test_content_no_explicit_body_tag():
    """ if a <body> tag is not specified, anything that is not
    a <head> is treated as the body."""
    hfr = HtmlFileReader('no_filename')

    html_frag = """
    <head>
      <title>Gandalf</title>
    </head>
    <div>
        <p>Bilbo Baggins</p>
        <p>Bard the Bowman</p>
        <p>Thorin Oakenshield</p>
    </div>
    """
    expected = '''<div>
<p>Bilbo Baggins</p>
<p>Bard the Bowman</p>
<p>Thorin Oakenshield</p>
</div>
'''
    parts = hfr.parse_html(html_frag)
    assert parts['content'] == expected


def test_content_without_body():
    """ If you don't have any content in your page at all;
    you'll get this message."""
    hfr = HtmlFileReader('no_filename')

    html_frag = """
    <head>
      <title>Gandalf</title>
    </head>
    """
    parts = hfr.parse_html(html_frag)
    assert parts['content'] == '[[YOUR CONTENT SHOULD GO HERE]]'


def test_read_title_tag():
    hfr = HtmlFileReader('no_filename')

    html_frag = """
    <head>
      <title>Gandalf</title>
      <body>hi</body>
    """
    parts = hfr.parse_html(html_frag)

    # Ensure both ways of reading titles are available
    assert parts['title'] == 'Gandalf'
    assert parts['meta']['title'] == 'Gandalf'


def test_missing_title_tag():
    hfr = HtmlFileReader('no_filename')
    html_frag = """
    <head>
      <h1>Gandalf</h1>
      <body>hi</body>
    """
    parts = hfr.parse_html(html_frag)
    assert parts['title'] == '[[NO TITLE FOUND]]'


def test_read_metadata():
    hfr = HtmlFileReader('no_filename')
    html_frag = """
    <head>
      <title>Gandalf</title>
      <meta name="categories" content="hobbit, lotr"/>
      <body>Hi</body>
    """
    parts = hfr.parse_html(html_frag)

    # Category is a special case; it gets converted to "categories"
    assert parts['meta']['categories'] == 'hobbit, lotr'


def test_read_category_metadata():
    # Category is a special case; it gets converted to "categories"
    hfr = HtmlFileReader('no_filename')
    html_frag = """
    <head>
      <title>Gandalf</title>
      <meta name="category" content="hobbit"/>
      <body>Hi</body>
    """
    parts = hfr.parse_html(html_frag)

    assert parts['meta']['categories'] == 'hobbit'


def test_bad_meta_tag():
    hfr = HtmlFileReader('no_filename')
    # This meta tag doesn't have a "content" attribute.
    html_frag = """
    <head>
      <title>Gandalf</title>
      <meta name="tags" value="hobbit"/>
      <body>Hi</body>
    """
    parts = hfr.parse_html(html_frag)

    # No category stuff, and we should NOT throw an exception
    assert 'tags' not in parts['meta']


def test_custom_theme():
    hfr = HtmlFileReader('no_filename')
    # This meta tag doesn't have a "content" attribute.
    html_frag = """
    <head>
      <title>Gandalf</title>
      <meta name="theme" content="lotr"/>
      <body>Hi</body>
    """
    parts = hfr.parse_html(html_frag)

    # No category stuff, and we should NOT throw an exception
    assert 'theme' in parts['meta']
    assert parts['meta']['theme'] == 'lotr'


# --------------
# get_back_path()
# --------------
def test_back_path_two_subdirs():
    """ get_back_path takes a file path and returns
       the necessary path to return to the root dir. """
    actual = get_back_path("/foo/bar")
    assert actual == "../../"


def test_back_path_double_slash():
    # double forward-slashes get corrected
    actual = get_back_path("/foo//bar")
    assert actual == "../../"


def test_back_path_with_leading_dot_slash():
    # Paths starting with a ./
    actual = get_back_path("./aaa/bbb")
    assert actual == "../"


# --------------
# get_template()
# --------------
def test_get_template():
    # Getting the template from config
    default_template_name = "common.thtml"
    template = get_template_name({})
    assert template == default_template_name


def test_get_template_from_metadata():
    # Getting the template from the content metadata.
    metadata_template_name = "aaaa"
    article_data = {'meta': {'template': 'aaaa'}}
    template = get_template_name(article_data)
    assert template == metadata_template_name


# --------------
# get_theme()
# --------------
def test_get_theme_from_metadata():
    article_data = {'meta': {'theme': 'pony'}}
    theme = get_theme_name(article_data)
    assert theme == 'pony'


def test_get_theme_from_default():
    article_data = {'meta': {'template': 'abababa'}}
    theme = get_theme_name(article_data)
    assert theme == '_not_set_'  # the hard-wired default


# ----------------------------
# html_encode
# ----------------------------
# TODO: change these so html_encode returns a str not a bytes
def test_html_encode_plain_ascii():
    assert b"3.49" == html_encode("3.49")


def test_html_encode_pound_sterling():
    assert b"&#163;3.49" == html_encode(u"£3.49")


def test_html_encode_less_than():
    # This is valid ASCII
    assert b"aa < bb" == html_encode("aa < bb")


def test_html_encode_html():
    # This is valid ASCII
    assert b"aa <b>bold</b> bb" == html_encode("aa <b>bold</b> bb")


# ----------------------------
# fix_incomplete_html
# ----------------------------
def test_fixing_html():
    input_str = """<div>bla bla <ul><li>item 1"""
    expected = """<div>bla bla <ul><li>item 1</li></ul></div>"""
    inner_body = fix_incomplete_html(input_str)
    assert inner_body == expected


def test_broken_html_unclosed_tag():
    # Ensure an unclosed tag e.g. '<li' gets fixed.
    input_str = """<div>hello<ul><li"""

    # html5lib => <div>hello<ul></ul></div>
    expected = """<div>hello<ul><li></li></ul></div>"""
    inner_body = fix_incomplete_html(input_str)
    assert inner_body == expected


def test_fix_incomplete_html_multiple_space_preserved():
    # Ensure an unclosed tag e.g. '<li' gets fixed.
    input_str = """<div>Go to <a href="#top">Top</a> of page.<p></p></div>"""

    expected = input_str
    fixed_html = fix_incomplete_html(input_str)
    assert fixed_html == expected


def test_fix_incomplete_html_pre():
    """ Test that multiple spaces in a <pre> tag are preserved when fixing
    broken/incomplete HTML.
    """
    input_str = """<pre>
Verse:
C                 F         C
Amazing grace how sweet the sound
     C                   G
That saved a wretch like me
  C                  F       C
I once was lost, but now I'm found
    C         G     C
Was blind but now I see
</pre><ul><li"""
    missing_end = '></li></ul>'

    expected = input_str
    fixed_html = fix_incomplete_html(input_str)
    assert fixed_html == expected + missing_end

#
# -------------------------------------------
#
#          S Y S T E M   T E S T S
#
# -------------------------------------------
#
# The following will need to be System tests, as they interact
# with the filesystem
#   mkdir_p()
#   read_site_config()
#


def create_temporary_filename():
    """ temp files are prefixed awcm_ to make it easier to identify
    and delete them.

    if you need to delete the temporary files:

    for d in $(ls -tr $TMPDIR | grep awcm_ ); do
        rm -r $TMPDIR/${d};
    done
    """
    root = tempfile.gettempdir()
    chars = string.ascii_letters + string.digits + ".-_:=@^"
    filename = 'awcm_' + ''.join(random.choice(chars) for _ in range(64))
    return os.path.join(root, filename)


def test_create_temporary_filename():
    aa = create_temporary_filename()
    bb = create_temporary_filename()
    print("")
    print(aa)
    print(bb)
    assert len(aa) == 64 + len(tempfile.gettempdir()) + 6
    assert len(bb) == 64 + len(tempfile.gettempdir()) + 6
    assert aa != bb  # chances of them being the same are extremely remote


# --------------
# mkdir_p()
# --------------
@pytest.mark.filterwarnings('ignore: tempnam')
def test_mkdir_p():
    """mkdir_p creates a folder if it does not exist.
    It does NOT create subfolders.

    pytest.mark.filterwarnings is used above these tests to suppress the
    warning that 'tempnam is a potential security risk to your program'
    """

    temp_dir_name = create_temporary_filename()
    assert not os.path.exists(temp_dir_name)
    mkdir_p(temp_dir_name)
    assert os.path.exists(temp_dir_name)
    
    # Tidy up
    os.rmdir(temp_dir_name)


@pytest.mark.filterwarnings('ignore: tempnam')
def test_mkdir_p_does_not_create_subdirs():
    """ mkdir_p does not create multiple subdirs at once.
    Attempting to do so will result in an OSError """
    temp_dir_name = create_temporary_filename()
    long_path = os.path.join(temp_dir_name, 'aaa', 'bbb')
    assert not os.path.exists(temp_dir_name)
    # assert this raises an OSError
    with pytest.raises(OSError):
        mkdir_p(long_path)


# --------------
# read_site_config()
# --------------
@pytest.mark.filterwarnings('ignore: tempnam')
def test_read_site_config_local_cfg():
    """ Test we can load site config.
    and that it sets a theme.
    """
    temp_dir_name = create_temporary_filename()
    os.mkdir(temp_dir_name)
    os.chdir(temp_dir_name)
    with open('config.json', 'w') as fh:
        fh.write('{"theme":"aaa"}')
    read_site_config()
    assert CONFIG['theme'] == 'aaa'

    # Tidy up
    os.remove(os.path.join(temp_dir_name, 'config.json'))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)


@pytest.mark.filterwarnings('ignore: tempnam')
def test_read_site_config_cfg_in_parent_dir():
    """ Test we can load site config with a relative dir.
    Create the config in one dir, then cd into a subdir and
    see if we can read the config, when adding the '..' arg.
    """
    temp_dir_name = create_temporary_filename()
    os.mkdir(temp_dir_name)
    os.mkdir(os.path.join(temp_dir_name, 'sub1'))
    os.chdir(temp_dir_name)
    with open('config.json', 'w') as fh:
        fh.write('{"theme":"abc"}')
    os.chdir(os.path.join(temp_dir_name, 'sub1'))
    read_site_config('..')
    assert CONFIG['theme'] == 'abc'

    # Tidy up
    shutil.rmtree(os.path.join(temp_dir_name, 'sub1'))
    os.remove(os.path.join(temp_dir_name, 'config.json'))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)


@pytest.mark.filterwarnings('ignore: tempnam')
def test_no_config_file_raises_exception():
    """ Test that, if a config file doesn't exist, we get an exception."""
    temp_dir_name = create_temporary_filename()
    os.mkdir(temp_dir_name)
    os.chdir(temp_dir_name)
    # 'forget' to create the config file right here.
    with pytest.raises(Exception):
        read_site_config()

    # Tidy up
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)


@pytest.mark.filterwarnings('ignore: tempnam')
def test_config_doesnt_have_theme():
    """ Test that, if the config does not specify a theme, we get
    an exception."""
    temp_dir_name = create_temporary_filename()
    os.mkdir(temp_dir_name)
    os.chdir(temp_dir_name)
    with open('config.json', 'w') as fh:
        fh.write('{"colour":"red"}')
    with pytest.raises(KeyError):
        read_site_config()

    # Tidy up
    os.remove(os.path.join(temp_dir_name, 'config.json'))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)


@pytest.mark.filterwarnings('ignore: tempnam')
def test_config_can_specify_default_template():
    """ Test that the config can also specify a template file..
    """
    temp_dir_name = create_temporary_filename()
    os.mkdir(temp_dir_name)
    os.chdir(temp_dir_name)
    with open('config.json', 'w') as fh:
        fh.write('{"theme":"asdfgh","default_template":"qwerty"}')
    read_site_config()
    assert CONFIG['theme'] == 'asdfgh'
    assert CONFIG['default_template'] == 'qwerty'

    # Tidy up
    os.remove(os.path.join(temp_dir_name, 'config.json'))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)

# make_pages_from_templates()
#    has to be a system test, as we read from and write to files.
#
#    get_all_filenames - needs to be a system test
#         N.B. doesn't work with '.' as an arg.
#
#   copy_static_files
#
#   HtmlFileReader.load()
#   HtmlFileReader.read()
#       lots of filesystem interaction.
#   TemplateWriter.read()
#   TemplateWriter.write()
#       TemplateWriter could take a custom jinja2 loader for
#       testing purposes.
#
# Maybe these should be in an object related to the generated files.
# They also have a lot of system interaction.
#   get_tag_or_category_as_html()
#   get_tag_list_as_html()
#   get category_list_as_html()


@pytest.mark.filterwarnings('ignore: tempnam')
def test_template_writer_validate_template_with_missing_file():
    """Verify that validate_template tells us about missing files

    """
    # SETUP; create common.thtml, but not navigation.thtml
    temp_dir_name = create_temporary_filename()
    _templates_dir = os.path.join(temp_dir_name, 'themes/x/templates')
    os.makedirs(_templates_dir)
    with open(os.path.join(_templates_dir, 'common.thtml'), 'w') as fh:
        fh.write("<p>")

    # THE TEST
    tw = TemplateWriter(templates_dir=os.path.join(temp_dir_name, 'themes'))
    assert tw.validate_template('x') is False
    # Might be good to capture the print()ed text?

    # Tidy up
    shutil.rmtree(os.path.join(temp_dir_name, 'themes'))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)


@pytest.mark.filterwarnings('ignore: tempnam')
def test_template_writer_validate_template_with_all_files_present():
    """Verify that validate_template reports OK if all files are present.
    """
    # SETUP; create common.thtml, but not navigation.thtml
    temp_dir_name = create_temporary_filename()
    _templates_dir = os.path.join(temp_dir_name, 'themes/x/templates')
    os.makedirs(_templates_dir)
    for tmpl in ['common.thtml', 'navigation.thtml']:
        with open(os.path.join(_templates_dir, tmpl), 'w') as fh:
            fh.write("<p>")

    # THE TEST
    tw = TemplateWriter(templates_dir=os.path.join(temp_dir_name, 'themes'))
    assert tw.validate_template('x') is True

    # Tidy up
    shutil.rmtree(os.path.join(temp_dir_name, 'themes'))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.rmdir(temp_dir_name)


if __name__ == '__main__':
    print("You should be using pytest!")
