#!/bin/bash

echo "Creating a sample HTML page"
cat > ./content/index2.html << 'EOF'
<head>
    <title>About</title>
    <!-- every page needs a title, which will usually also be the
         H1 heading -->

    <meta name="date" content="2015-04-24 10:00" />
    <meta name="summary" content="About Andy's Saxophone pages" />
    <meta name="tags" content="tenor" />
        <!-- all other metadata tags are specified like this -->


    <meta name="category" content="misc" />
    <!-- You can specify tags and categories. How they get used will be
         determined by the theme templates-->

    <meta name="template" content="navigation" />
    <!-- Any page can specify a custom template from the theme. (this is
         one of the reasons I wrote AWCM, because I couldn't find another
         static-content-generator that could do this) -->
</head>
<body>
This is an example page craeted with create_sample_content.sh<br>
You will want to put your own stuff here.
</body>
EOF


echo "Creating a sample config"
cat > ./config.json << 'EOF'
{
    "theme": "womble"
}
EOF

cp -r /path/to/example/theme/womble ./themes/