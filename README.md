

# Instructions on using AWCM

AWCM - an Awesome *(cough)* static content generator.

## About AWCM
AWCM - Andy's Web Content Manager - is a static HTML website generator,
inspired by the Jekyll and Pelican website generators. It's pronounced 
"Awesome" — I'll let you decide if it's awesome or not.

For the **quick setup instructions** scroll to the bottom of the page

## Features
* All links are relative: (which means AWCM can work on file:// paths)
* Themes, just like Wordpress, Jekyll, Pelican etc.
* Builds navigation pages, like Pelican does. (they're static HTML files, and do what the navigation pages on Wordpress do)
* A page can specify that it should use a different template file
* A page can specify that it should use a specific theme
* Supports tags and categories, like Wordpress and Pelican
* Plugin support to allow content to be built programmatically

## Requirements
* Python
* Jinja2
* Beautifulsoup
* LXML
 
Install Python, then use 'pip' (the Python package installer) to add the other
dependencies

```$ pip install jinja2 bs4 lxml```

The script `setup_awcm.sh` (in the bits_box folder) handles this for you.

It is designed for Linux-like systems (including MacOS).

It may work on Windows but I haven't tested it; you will need Python, Bash and
Make (I suggest trying it under Cygwin)

## How it works
Web pages can either be a made up from a single piece of content, or can be
generated from lots of little bits we'll call "components". 

The source material used to create (whole) web pages is in the "content/"
folder 

The source material used to build pages from components is stored in the
"components/" folder. These "generated pages" are constructed from the
"components" and saved in the folder "_meta/" 

"pages" in "content/" and "generated pages" in "_meta"/ are then merged with
the appropriate theme template (a "skin" if you like) to generate the resultant
HTML page in the "output/" folder. You need to specify the default theme name
in a file called 'config.json'. 

Examples of components are parts of a page that are combined with other
components to form a page, or maybe a sidebar that appears on one or more
pages. 

Theme files are stored in the "themes/" folder, and include both templates
(used to generate HTML) and static files (e.g. CSS, images and Javascript
files). 

## Creating Content
Content files are just HTML - plain old, simple HTML.

Note, I really do mean *just* HTML: don't try to add scripts and CSS in the
HEAD section; they'll get ignored.

Somethings are allowed in the HEAD section of your content, notably the page
title, summary, creation date, and the tags and categories to which your
article belongs

Here is an example of the **head** section

```
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
```

The BODY can contain any HTML, and of course you can give your tags CSS
classes and IDs. (The CSS definition goes in the template.)

The content should include the full top-level tags, so the outline of a
content document will look like this:

```
<html>
    <head>
        <!-- title and meta as described above -->
        <title>...</title>
        <meta ... />
    </head>
    <body>
        content here <br>
    </body>
</html>
```

The static content generator will take a copy of the appropriate template,
(as described in the settings file, and possibly meta tags), and insert the
content from within the BODY tags, to create the generated page.

You can put small snippets of CSS and Javascript in the Body, but you should
keep this as small as possible. As a general rule, Javascript function
definitions should go in the theme.

**Note** There must be at least one HTML tag inside the \<body\> section.
A trailing \<br\> will work, as in the example above.

## Components
Components are constructed as follows:

1. Any executable program in the "components/" folder that starts with 3
   digits followed by either an underscore or a hyphen is executed (they are 
   executed in numerical order). Each one writes its data to the "_meta/"
   folder; either writing an unthemed HTML page or a data file.

1. There are two ready-made component generators (000_collect_data.py and 
   999_mksitemap.py) which are used to build the navigation pages (sitemap,
   category listings and tag listings). 000_collect_data.py generates a set
   of JSON-encoded data files in "_meta/", and 999_mksitemap.py uses these
   data files to construct unthemed HTML files
   
1. Any other component generator can be written that may modify the
   JSON-encoded data files. (e.g. to add to a sitemap) Component generators 
   can be written in any programming language that may be available on your
   system. Writing your component generator in Python give you the advantage
   of using library functions from AWCM itself.
   
1. This system works on Linux-like systems (including MacOS) and takes
  advantage of the hash-bang syntax for script execution.

Source material in the "content/" folder should be HTML, but must not need to
include CSS or Javascript in the HEAD. Instead, META tags in the HEAD section
are used to specify tags, categories, the title etc. 

## The config.json file
At the top level of your project, you need a configuration file called 
`config.json`. It should be a simple JSON object. 

The minimal config looks like:

```json
{
    "theme": "womble"
}
```
The following keys are recognised:
* theme (mandatory)
* default_template (optional)

## Hiding pages
If a page does not contain any 'tag' or 'category' entries, it will not
appear in the automatically generated navigation pages.

You can use this to your advantage if you want to generate pages that do not
appear in the navigation areas.

Such pages will only be accessible if you create your own link to them from
another page, or to someone who knows the address of the page.

## Themes and Templates

### Themes

You will need at least one theme to make your website.

The theme is a collection of HTML Templates, and static files (CSS,
Javascript, images etc) used to customise the appearance of the website.
These all reside in the "themes/" folder, under the name of the theme.

The file structure for a theme looks like this. Let's assume the theme is
called "Womble"

```
config.json
themes/
      womble/
            static/
                  background.png
                  some_styles.css
            templates/
                  common.thtml
                  navigation.thtml
content/
components/
```

The name of default theme ('womble' in this example) must be defined in the
file 'config.json'.

When the pages are generated, the static files from the theme will be placed
in a folder called "themes/womble/". This allows you to have have several
themes in action on the same website.

The templates, e.g. common.thtml, are Jinja2 templates which should provide
the "outer" HTML of a page.

Inside a template, the following Jinja2 tokens are available; The content 
generator injects values such as the **title** and **article** from the content
file in in the place of these tokens in curly brackets

* `{{ title }}` the page title
* `{{ article }}` the article (the main content of the page)
* `{{ back_path }}` a relative URL path back to the home folder
* `{{ theme_path }}` a relative URL to the current theme files, specifically
  so you can refer to files in the theme. For example, to refer to a CSS
  file, you could use 
`<link rel="stylesheet" href="{{ theme_path }}style.css" media="all">`
* `{{ tags_html }}` and `{{ categories_html }}` are replaced by the HTML
  listing the tags and categories, respectively

The default theme must be defined in the file 'config.json'. In the example
above, the contents of this file will look like this (ensure the curly
braces, quotes and colon are exactly as here):

```json
    { "theme": "womble" }
```

Individual pages can specify which theme they would like to use. To accomplish
this, add a tag like `<meta name="theme" content="my_theme_name" />` to your
document.

A page can be drawn using a specific template as well, by adding a 
"template" meta-tag, for example 
`<meta name="template" content="my_new_template" />` If the specified template
does not exist, the default template 'common.thtml' will be used instead.

### Templates
Templates have a file suffix of "thtml"

The default template is "common.thtml"; if no other template is specified,
"common.thtml" is used.

Navigation pages will use a template called "navigation.thtml"

Any page can specify a separate template in a <meta> tag, e.g. 
`<meta name="template" content="landing" />` would cause this page to be 
rendered with the template "landing.thtml" (the ".thtml" will be appended
if it's not specified in the <meta> tag.)

Any page can use the "navigation.thtml" template if desired.

If desired, the default template can be configured in the 'config.json' file.

## Quick Setup

Download and run the setup script from the 
[github repository](https://github.com/andywis/static-content-generator)
as follows:
* `mkdir a_new_folder && cd a_new_folder`
* `curl -O https://raw.githubusercontent.com/andywis/static-content-generator/master/bits_box/setup_awcm.sh`
* `bash ./setup_awcm.sh`

Then create your website:
* Add content to the `content/` folder
* Add a theme to the `themes/` folder
* Run `make`
* The generated content will be created in `output/`. Load it in a browser

