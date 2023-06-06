#!/bin/sh

set -e

lilypond --loglevel=ERROR --output=extension - <<EOS
\paper {
  top-margin = 0
  left-margin = 0
  right-margin = 0

  bookTitleMarkup = ##f
  scoreTitleMarkup = ##f
  oddHeaderMarkup = ##f
  oddFooterMarkup = ##f
  evenHeaderMarkup = ##f
}

#(ly:set-option 'crop #t)

\markup {
  \overlay {
    \with-color "#478eb8" \draw-circle #2 #0 ##t
    \with-color "#9ccc7c" {
      \translate #'(-0.1 . 0) \musicglyph #"noteheads.s2"
      \override #'(thickness . 2)
      \translate #'(0 . -0.24) \draw-line #'(0 . -1.75)
    }
    \with-color "#69a540" \draw-circle #2.05 #0.1 ##f
  }
}
EOS

convert -density 300 extension.cropped.pdf -resize 70% LilyPond.novaextension/extension@2x.png
convert LilyPond.novaextension/extension@2x.png -resize 50% LilyPond.novaextension/extension.png

rm -f extension.cropped.pdf extension.pdf extension.cropped.png
