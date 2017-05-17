#!/bin/sh
# usage:
# ./markdown2html.sh input_file.md output_file.html

TEMPBODY="body.tmp"
STYLEHEAD="style-chunk.html"
FILEIN="$1"
FILEOUT="$2"

# mark it down, add the style-chunk header
# and close it off neatly with a little </body></html>

markdown -o "$TEMPBODY" "$FILEIN" && \
cat "$STYLEHEAD" > "$FILEOUT" && \
cat "$TEMPBODY" >> "$FILEOUT" && \
rm "$TEMPBODY" && \
echo "</body></html>" >> "$FILEOUT"
