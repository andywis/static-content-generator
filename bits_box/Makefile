# Make web pages using the AWCM static content generator


GENERATOR_SCRIPTS=$(shell ls components | egrep '^\d\d\d[-_]')

all: generated web
.PHONY: all generated web


generated:
	@echo "Making auto-generated pages"
	@source _tmp/venv/bin/activate && \
	for s in ${GENERATOR_SCRIPTS}; do \
	    if [ -x "components/$$s" ]; then \
	        echo $$s; \
	        (cd components; ./$$s) \
	    fi; \
	done
	@echo " "

web:
	@echo "Templatising all pages"
	source _tmp/venv/bin/activate && \
	python -c "from awcm import awcm; awcm.main()"

# Backticks or $()
#	- must be OUTSIDE any target
#   - $() doesn't appear to work, but $(shell ...) does
#	- Backticks is evaluated within the target
#   - $(shell ...) is evaluated immediately
#
# Loops:
#	shell variable inside the loop needs double $ to escape Makefile meaning
