#!/bin/bash

# Make all the components
# In the initial version, we'll use bash to make this amazingly simple.

# Any files matching *.sh will be executed -- if they are executable.
#
# By convention, the executable script should be named following this pattern:
#      \d\d\d_name.sh
#      e.g. 001_tvc.sh
# If they use any data, it should be in a folder inside components/ called
# by the same name, 
#      e.g. tvc/
#
# They should write content to "../_meta/<some filename>.html",
#      e.g. ../_meta/tvc.html
#
# The generated content in _meta/ should contain a <body> tag and <title> tag at minimum.
# the content may also contain any other meta tags to control the theme template etc.
#
# You can, of course, use something other than bash in your component generator;
# just change the shebang line as you see fit. See 003_joke.sh
#
#
cd components

for file in $(ls *.sh)
do 
    if [ -x "$file" ]
    then
        echo RUNNING $file
        ./$file
    else
        echo "IGNORING $file (not executable)"
    fi
done
