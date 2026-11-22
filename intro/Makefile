PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error

# intro.pdf: exercises at the end of each section. intro-reading.pdf: the text alone, exercises and solutions in
# two appendices. One source (intro.tex + exercises.tex); the reading version is built with \readingversion defined.
all: intro.pdf intro-reading.pdf

intro.pdf: intro.tex exercises.tex
	$(PDFLATEX) intro.tex
	$(PDFLATEX) intro.tex
	$(PDFLATEX) intro.tex

intro-reading.pdf: intro.tex exercises.tex
	$(PDFLATEX) -jobname=intro-reading '\def\readingversion{}\input{intro}'
	$(PDFLATEX) -jobname=intro-reading '\def\readingversion{}\input{intro}'
	$(PDFLATEX) -jobname=intro-reading '\def\readingversion{}\input{intro}'

clean:
	rm -f *.aux *.log *.out *.toc intro.pdf intro-reading.pdf
