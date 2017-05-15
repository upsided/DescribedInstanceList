#!/bin/sh

TEMPBODY="body.tmp"
STYLEHEAD="style-chunk.html"
FILEIN="$1"
FILEOUT="$2"

markdown -o "$TEMPBODY" "$FILEIN" && \
cat "$STYLEHEAD" > "$FILEOUT" && \
cat "$TEMPBODY" >> "$FILEOUT" && \
rm "$TEMPBODY" && \
echo "</body></html>" >> "$FILEOUT"
