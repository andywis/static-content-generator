#!/usr/bin/env python
# coding: utf-8
# Tests for AWCM (run with pytest ./tests.py)

from awcm.awcm import get_back_path, HtmlFileReader, \
    get_template_name, html_encode


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


# ----------------------------
# html_encode
# ----------------------------
def test_html_encode_plain_ascii():
    assert "3.49" == html_encode("3.49")


def test_html_encode_pound_sterling():
    assert "&#163;3.49" == html_encode(u"£3.49")


def test_html_encode_less_than():
    # This is valid ASCII
    assert "aa < bb" == html_encode("aa < bb")


def test_html_encode_html():
    # This is valid ASCII
    assert "aa <b>bold</b> bb" == html_encode("aa <b>bold</b> bb")

# ----------------------------
# make_pages_from_templates()
# ----------------------------
#  has to be a system test, as we read from and write to files.


# The following will need to be System tests, as they interact
# with the filesystem
#   mkdir_p - needs to be a system test
#    get_all_filenames - needs to be a system test
#   copy_static_files -
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

if __name__ == '__main__':
    print("You should be using pytest!")
