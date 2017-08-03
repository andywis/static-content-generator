#!/usr/bin/env python
# Tests for AWCM (see make.py)

from make import HtmlFileReader

def test_read_metadata():
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

    assert parts['title'] == 'Gandalf'

    expected = '''
<p>Bilbo Baggins</p>
<p>Bard the Bowman</p>
<p>Thorin Oakenshield</p>
'''
    assert parts['content'] == expected

    print parts['meta']


if __name__ == '__main__':
    test_read_metadata()
    print('OK')
