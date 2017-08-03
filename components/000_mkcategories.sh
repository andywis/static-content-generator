#!/bin/bash
#
# This is a "special" component generator. The generated content
# is injected into templates. (or at least, it _will_ be!!)

# ----------------------------------------------------------------------------
# Construct a sitemap of all "real" pages 
# (N.B. doesn't include the generated pages)
# ----------------------------------------------------------------------------
out_file=../_meta/000_all_files.html
echo "<title>Sitemap</title><body><div><ul>" > $out_file

all_files=$(cd ../content; find . -name '*.html')
for file in $all_files;
do
    link_text=$(grep '<title>' ../content/$file | sed -e 's,<title>,,' | sed -e 's,</title>,,' 2>/dev/null)
    echo "<li><a href=\"$file\">$link_text</a></li>" >> $out_file
done

echo "</ul></div></body>" >> $out_file


# TODO: fish the categories out of each page
#       (may need to be done in Python)
#       create a *set* of 000_<categoryname> pages.
#     - then get the categories injected into the template(s)
