#!/bin/sh

# Exit immediately if a command exits with a non-zero status or an undefined
# variable is used.
set -eu

Nova_path=${1:-/Applications/Nova.app}

cp tree-sitter-lilypond/queries/highlights-builtins.scm \
   tree-sitter-lilypond/queries/highlights.scm \
   tree-sitter-lilypond/queries/injections.scm \
   LilyPond.novaextension/Queries/lilypond

cp tree-sitter-lilypond/queries/highlights-scheme-builtins.scm LilyPond.novaextension/Queries/lilypond_scheme/highlights-builtins.scm
cp tree-sitter-lilypond/queries/highlights-scheme-lilypond-builtins.scm LilyPond.novaextension/Queries/lilypond_scheme/highlights-lilypond-builtins.scm
cp tree-sitter-lilypond/queries/highlights-scheme.scm LilyPond.novaextension/Queries/lilypond_scheme/highlights.scm

make_parser () {
  build_path="$1/build"
  mkdir -p "$build_path"

  flags="-arch arm64 -arch x86_64 -mmacosx-version-min=11.0 -I$1/src"

  SRC_DIR="$1/src" \
  PARSER_NAME=$2 \
  PREFIX="$build_path" \
  CFLAGS="$flags -O3" \
  CXXFLAGS="$flags -O3" \
  LDFLAGS="$flags -F$Nova_path/Contents/Frameworks/ -framework SyntaxKit -rpath @loader_path/../Frameworks" \
  make --environment-overrides

  codesign --sign '-' "libtree-sitter-$2.dylib"

  mv "libtree-sitter-$2.dylib" LilyPond.novaextension/Syntaxes
  rm "$1/src/parser.o"
}

make_parser tree-sitter-lilypond/lilypond lilypond
make_parser tree-sitter-lilypond/lilypond-scheme lilypond_scheme
