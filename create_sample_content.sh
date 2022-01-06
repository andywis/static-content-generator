#!/bin/bash

mkdir -p content

echo "Creating a sample HTML page"
cat > ./content/index_sample.html << 'EOF'
<head>
    <title>Sample Page</title>
    <!-- every page needs a title, which will usually also be the
         H1 heading -->

    <meta name="date" content="2015-04-24 10:00" />
    <meta name="summary" content="Some information about the page goes here" />
    <meta name="tags" content="sample" />
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
This is an example page created with create_sample_content.sh<br>
You will want to put your own content here.
<p>
Note that the homepage (<a href="./index.html">index.html</a>) is
auto-generated from the script in components/001/make_homepage.py.
The homepage shows a summary of other pages.
<p>
You can use the &lt;meta&gt; tags in a content file to control how the
page is rendered. For example, you can add tags and categories (this
page has a tag "sample" and a category "misc". See the source code for
this page for more details.
<p>
The background of this page is yellow because there is a &lt;meta&gt; tag
specifying that the template to use is "navigation". The navigation
template loads n.css, which specifies a yellow background.
<p>
There are some generated pages for tags, categories etc. These also use
the "navigation" template.
</body>
EOF

mkdir -p themes/womble/templates
mkdir -p themes/womble/static
cat > ./themes/womble/templates/common.thtml << 'EOF'
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
        
    <!-- this will load b.css from themes/womble/static/b.css-->
    <link rel="stylesheet" href="{{ theme_path }}b.css" media="all">
</head>
<body>
    <!-- back_path provides a means to get back to the root folder -->
    <p><a href="{{ back_path }}index.html">Home</a></p>
    <div class="content">
        <h1><a href="#">{{ title }}</a></h1>

        <!-- Template injects content here -->

        {{ article }}

        <!-- End of injected content block -->
           
    </div>

    <!-- show page tags and categories in the footer -->
    <div class="footer-tags">
        <h3>Tags</h3>
        {{ tags_html }}
    </div>
    <div class="footer-categories">
        <h3>Categories</h3>
        {{ categories_html }}
    </div>
</body>
</html>
EOF

# Copy the theme template to navigation.thtml but change the CSS file
sed -e 's/b.css/n.css/g' < ./themes/womble/templates/common.thtml > \
     ./themes/womble/templates/navigation.thtml

# Create the CSS files
echo 'body {background-color: #ddd;}' > ./themes/womble/static/b.css

# n.css (for navigation pages) has a yellower background
echo 'body {background-color: #ffd;}' > ./themes/womble/static/n.css

echo "Creating a sample config"
cat > ./config.json << 'EOF'
{
    "theme": "womble"
}
EOF

echo "Now generate your content by typing \`make\`"
