#!/bin/sh

PWD=`pwd`
SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASENAME="${SOURCE_DIR}/data/DescribedInstances"

cd "$SOURCE_DIR"

if ! chmod +x tools/markdown2html.sh; then # just cuz
    cd $PWD
    exit 1
fi

mkdir -p "${SOURCE_DIR}/data/"

if ! python3 tools/federation2json.py "${BASENAME}.json"; then
    cd $PWD
    exit 1
fi

if ! python3 tools/json2markdown.py "${BASENAME}.json" "${BASENAME}.md"; then
    cd $PWD
    exit 1
fi

if ! python3 tools/json2sqlite.py "${BASENAME}.json" "${BASENAME}.sqlite"; then
    cd $PWD
    exit 1
fi

cd "$SOURCE_DIR/tools"
if ! ./markdown2html.sh "${BASENAME}.md" "${BASENAME}.html"; then
    cd $PWD
    exit 1
fi

cd "$PWD"