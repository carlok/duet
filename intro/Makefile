PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error

# intro.pdf: the text (definitions, examples, theorems, proofs). exercises.pdf: exercises by section of the text, with
# solutions. Both use preamble.tex. exercises.tex reads the text's labels from intro.aux, so intro is built first.
all: intro.pdf exercises.pdf

intro.pdf: intro.tex preamble.tex
	$(PDFLATEX) intro.tex
	$(PDFLATEX) intro.tex
	$(PDFLATEX) intro.tex

exercises.pdf: exercises.tex preamble.tex intro.pdf
	$(PDFLATEX) exercises.tex
	$(PDFLATEX) exercises.tex
	$(PDFLATEX) exercises.tex

clean:
	rm -f intro.aux intro.log intro.out intro.toc exercises.aux exercises.log exercises.out intro.pdf exercises.pdf   # not checks.out
