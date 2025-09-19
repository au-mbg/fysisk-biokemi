.PHONY: master student all

FMT ?=

ifdef FMT
TO_FLAG := --to $(FMT)
endif


master:
	quarto render --profile master $(TO_FLAG)

student:
	quarto render --profile student $(TO_FLAG)

site-master:
	quarto render --profile site-master --quiet

site-student:
	quarto render --profile site-student --no-clean
	cp redirect/index.html _site-combined/index.html

website: site-master site-student

all: master student

clean:
	rm -rf _master _student _site _site-combined
	rm -rf lessons/*html lessons/*.ipynb lessons/*_files lessons/.ipynb_checkpoints
	rm -rf quizzes/*.html quizzes/*.ipynb quizzes/*_files quizzes/.ipynb_checkpoints
