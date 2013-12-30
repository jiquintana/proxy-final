#!/bin/bash
OUTPUTDIR=./doc
mkdir -p $OUTPUTDIR/html $OUTPUTDIR/pdf
epydoc -v --html -o $OUTPUTDIR/html --inheritance listed --graph all *.py
epydoc -v --pdf -o $OUTPUTDIR/pdf --inheritance listed --graph all *.py
