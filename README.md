# Described Instance List Tools
This is a set of tools for generating information, including descriptions, on every [Mastodon](https://en.wikipedia.org/wiki/Mastodon_Social) instance, in various formats, like sqlite and html.

#### tl;dr
`chmod +x buildall.sh && buildall.sh`
Look in the data/ directory for your generated files.

### Dependencies
Oh wow, library errors? This is maybe why. You need:

* Python 3
* `pip3 install bs4` BeautifulSoup, for parsing HTML
* `pip3 install requests`, for downloading websites without silly syntactic junk


### The Scripts

| Script | Effect | output file |
|--------|--------|--------|
|tools/federation2json.py | downloads and generates .json database | data/DescribedInstances.json |
|tools/json2markdown.py | generates a markdown file from the .json database, above | data/DescribedInstances.md |
|tools/json2html.py | generates an HTML file from .json file, above  | data/DescribedInstances.html |
|tools/json2sqlite.py | generates an sqlite database of the .json file, above | data/DescribedInstances.sqlite |
|buildall.sh | generates all of the above | data/* |

### Warning
These tools are *ad hoc kludges* to get the job done only. This is a simple one-shot tool that you can run for 30 minutes to consume all the info out there. I may turn this into a more interruption-friendly database updater later.


### Use

If you wish to generate all files, simply:
```
chmod +x buildall.sh && ./buildall.sh
```

If you wish to generate each file individually:
```
cd tools
python3 federation2json.py ../data/DescribedInstances.json
# wait about 30 minutes for stuff to download
python3 json2markdown.py ../data/DescribedInstances.json ../data/DescribedInstances.md
python3 json2html.py ../data/DescribedInstances.json ../data/DescribedInstances.html
python3 json2sqlite.py ../data/DescribedInstances.json ../data/DescribedInstances.sqlite
```

This is pretty much what the `buildall.sh` script does.

### Tinkering
If you want to test a smaller set of random instance data, set the `TEST=1` environment variable, e.g.:
```
TEST=1 ./buildall.sh
```

or

```
cd tools/
TEST=1 python3 federation2json my_testdata.json
```

if you want to simply update a previous .json file (skipping the instance list download from mastodon.xyz):
```
JSON_FILE=data/DescribedInstances.json ./buildall.sh
```

Since you read this README all the way to the end, have a gift in federation2json.py:
```
THREADS_MAX = 50
```
Play nice! Cheers.