#!/bin/sh

BASENAME="../data/DescribedInstances"
if ! cd tools; then
    exit 1
fi

if ! chmod +x markdown2html.sh; then # just cuz
    exit 1
fi

mkdir -p ../data/

if ! python3 federation2json.py "${BASENAME}.json"; then
    exit 1
fi

if ! python3 json2markdown.py "${BASENAME}.json" "${BASENAME}.md"; then
    exit 1
fi

if ! python3 json2sqlite.py "${BASENAME}.json" "${BASENAME}.sqlite"; then
    exit 1
fi

if ! ./markdown2html.sh "${BASENAME}.md" "${BASENAME}.html"; then
    exit 1
fi