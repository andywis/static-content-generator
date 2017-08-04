
# To Do
After running "pip install -e .", I still have to run "pip install -r requirements". This can be fixed. How?


You can run the content generator from a Makefile like this:

```
web:
    source ~/venv/awcm/bin/activate && python -c "from awcm import awcm; awcm.main()"
```
(ensure you have leading tabs on the indented line!)
