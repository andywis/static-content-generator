#!/usr/bin/env python
# Tests for AWCM (see make.py)

from awcm.awcm import HtmlFileReader


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


if __name__ == '__main__':
    test_read_content()
    test_read_title_tag()
    test_read_metadata()
    test_read_category_metadata()
    test_bad_meta_tag()

    print('End')
