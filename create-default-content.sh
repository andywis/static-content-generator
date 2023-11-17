

THEME_NAME="simpletheme"

# Create a minimal config file.
if [ ! -f config.json ]; then
    echo "CREATING config.json"
    cat <<EOF > config.json
{
    "theme": "$THEME_NAME"
}
EOF
fi

# Create a minimal content file, if ./content is empty.
if [ -z "$(ls content)" ] ; then
    echo "CREATING an example content file: content/example_content.html"
    creation_date=$(date +'%Y-%m-%d %H:%M')
    cat << EOF > content/example_content.html
<html>
    <head>
        <title>A title</title>
        <meta name="date" content="${creation_date}" />
    </head>
    <body>
        <p>this is example content</p>
        <p>
           The source material used to create whole web pages is
           stored in the "content/" folder, just like this page.
        </p>
        <p>
            A page must have a &lt;title&gt; tag. Other page metadata
            can be specified using &lt;meta&gt; tags. See the source
            of this page for examples. Valid metadata tags are:
            date, summary, tags, categories and template (to specify
            an alternative template)
        </p>
        <p>
            Note There must be at least one HTML tag inside the &lt;body&gt;
            section. A trailing &lt;br&gt; will be enough.
        </p>
        <p>
            "pages" in the "content/" folder (and "generated pages"
            in "_meta"/) are then merged with the appropriate theme
            template to generate the resultant HTML pages, which are
            saved to the "output/" folder. The default theme is
            specified in the 'config.json' file.
        </p>
        <p>
        </p>
            For more information, see the
            <a href="https://github.com/andywis/static-content-generator"
            target="_blank">documentation in the GitHub Repository.</a>
    </body>
</html>
EOF
fi


# Make the folder structure for the theme
mkdir -p themes/$THEME_NAME/static
mkdir -p themes/$THEME_NAME/templates


if [ ! -f themes/$THEME_NAME/static/style.css ]; then
    echo "CREATING default CSS file in themes/$THEME_NAME/templates/"
    cat <<EOF > themes/$THEME_NAME/static/style.css
html {
    font-family: Arial, Helvetica, sans-serif;
}
EOF
fi

if [ ! -f themes/$THEME_NAME/templates/common.thtml ]; then
    echo "CREATING default theme files in themes/$THEME_NAME/templates/"
    cat <<EOF > themes/$THEME_NAME/templates/common.thtml
<DOCTYPE HTML>
<html>
    <head>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="{{ theme_path }}style.css" media="all">
    </head>
    <body>
        {{ article }}

        <hr>
        <div>
            <a href="{{ back_path }}">Link back to the homepage</a>
        </div>
        <div>
            Tags: {{ tags_html }}
        </div>
        <div>
            Categories {{ categories_html }}
        </div>
    </body>
</html>
EOF
fi

if [ ! -f themes/$THEME_NAME/templates/navigation.thtml ]; then
    echo "COPYING common.thtml to create navigation.thtml theme file."
    cp themes/$THEME_NAME/templates/common.thtml themes/$THEME_NAME/templates/navigation.thtml
fi

