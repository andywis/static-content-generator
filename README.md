
# To Do
After running "pip install -e .", I still have to run "pip install -r requirements". This can be fixed. How?


You can run the content generator from a Makefile like this:

```
web:
    source ~/venv/awcm/bin/activate && python -c "from awcm import awcm; awcm.main()"
```
(ensure you have leading tabs on the indented line!)


## To create a theme:
Create the folder structure as follows:

```
  mythemename
     static
     templates
         common.thtml
```
The "static" folder is for files that won't change, e.g. CSS and Javascript files.
The "templates" folder should contain "Jinja2" style templates, and at minimum needs
a templates file called common.thtml

Within the template, variables are injected with double-curly brackets. The content
generator injects values such as the **title** and **article** (the content) into
the page with these mechanisms. A simple
template might look like this; you would save the file "style.css" to the "static"
folder.

```
<html>
    <head>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="{{ theme_path }}style.css" media="all">
    </head>
    <body>
        <div class="wrapper">
            <div class="content">
                <h1>{{ title }}</h1>
                {{ article }}
            </div>
        </div>
    </body>
</html>
```
