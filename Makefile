# Makefile to build images from all scenario graphs

%.svg : %.dot
	dot -Tsvg $< > $@

%.png : %.dot
	dot -Tpng $< > $@

.PHONY: all
all: svgs pngs

.PHONY: svgs
svgs: multiple_resolution_by_html.svg journal_with_pdf_html.svg journal_with_pdf_html_img.svg plos_with_component_image.svg arxiv_no_item.svg arxiv_plan.svg dlib_article.svg vivo_person.svg ldp.svg

.PHONY: pngs
pngs: multiple_resolution_by_html.png journal_with_pdf_html.png journal_with_pdf_html_img.png plos_with_component_image.png arxiv_no_item.png arxiv_plan.png dlib_article.png vivo_person.png ldp.png
