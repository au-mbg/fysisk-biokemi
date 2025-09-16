.PHONY: master student all

FMT ?=

ifdef FMT
TO_FLAG := --to $(FMT)
endif


master:
	quarto render --profile master $(TO_FLAG)

student:
	quarto render --profile student $(TO_FLAG)

all: master student

clean:
	rm -rf _master _student
