%.svg : %.dot
	dot -Tsvg $< > $@

.PHONY: all
all: multiple_resolution_by_html.svg journal_with_pdf_html.svg plos_with_component_image.svg
