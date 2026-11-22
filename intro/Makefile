PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error

# intro-reading.pdf: the text alone. intro.pdf: the same text with exercises at the end of each section and
# solutions in an appendix. The text is in intro.tex, the exercises in exercises.tex; intro-reading.tex switches.
all: intro-reading.pdf intro.pdf

intro-reading.pdf: intro-reading.tex intro.tex exercises.tex
	$(PDFLATEX) intro-reading.tex
	$(PDFLATEX) intro-reading.tex
	$(PDFLATEX) intro-reading.tex

intro.pdf: intro.tex exercises.tex
	$(PDFLATEX) intro.tex
	$(PDFLATEX) intro.tex
	$(PDFLATEX) intro.tex

clean:
	rm -f *.aux *.log *.out *.toc intro.pdf intro-reading.pdf
