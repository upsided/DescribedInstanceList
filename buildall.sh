#!/bin/sh

PWD=`pwd`
SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASENAME="${SOURCE_DIR}/data/DescribedInstances"

cd "$SOURCE_DIR"

mkdir -p "${SOURCE_DIR}/data/"

if [ "$CRAWL" -eq "1" ] ; then
  if [[ -z "$JSON_FILE"  ]]; then
    export JSON_FILE="${BASENAME}.json"
    if ! python3 tools/InstanceSeer.py "${BASENAME}.json"; then
      cd $PWD
      exit 1
    fi
  else
    if ! python3 tools/InstanceSeer.py "$JSON_FILE"; then
      cd $PWD
      exit 1
    fi
  fi
fi


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

if ! python3 tools/TemplateRunner.py "${BASENAME}.json" "${BASENAME}"; then
    cd $PWD
    exit 1
fi

cd "$PWD"