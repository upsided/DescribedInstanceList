# Described Instance List Tools
This is a set of tools for generating information, including descriptions, on every listed [Mastodon](https://en.wikipedia.org/wiki/Mastodon_Social) instance, in various formats, like sqlite and html.

#### tl;dr
`chmod +x buildall.sh && buildall.sh`
Look in the data/ directory for your generated files.

### Dependencies
Oh wow, library errors? This is may be why. You need:

* Python 3
* `pip3 install bs4` BeautifulSoup, for parsing HTML
* `pip3 install requests`, for downloading websites without silly syntactic junk
* `pip3 install cheetah3`, for generating html


### The Scripts

| Script | Effect | output file |
|--------|--------|--------|
|tools/federation2json.py | downloads and generates .json database | data/DescribedInstances.json |
|tools/json2markdown.py | generates a markdown file from the .json database, above | data/DescribedInstances.md |
|tools/TemplateRunner.py | generates two HTML files from .json file, above  | data/DescribedInstances.html |
|tools/json2sqlite.py | generates an sqlite database of the .json file, above | data/DescribedInstances.sqlite |
|buildall.sh | generates all of the above | data/* |
|tools/AboutThisInstance.py | delivers the json descripton for a single instance | none |

### Warning
These tools are *ad hoc kludges* to get the job done only. This is a simple one-shot tool that you can run for 30 minutes to consume all the info out there. I may turn this into a more interruption-friendly database updater later.


### Use

To generate all files, simply:
```
chmod +x buildall.sh && ./buildall.sh
```

To generate each file individually:
```
cd tools
python3 federation2json.py ../data/DescribedInstances.json
# wait about 30 minutes for stuff to download
python3 json2markdown.py ../data/DescribedInstances.json ../data/DescribedInstances.md
python3 TemplateRunner.py ../data/DescribedInstances.json ../data/DescribedInstances
python3 json2sqlite.py ../data/DescribedInstances.json ../data/DescribedInstances.sqlite
```

This is pretty much what the `buildall.sh` script does.

### About This Instance
To see a json file describing an instance, try
```
python3 AboutThisInstance.py mastodon.social
```
This might be more useful than the monolithic approach above.

### Tinkering
To test a smaller set of random instance data, set the `TEST=1` environment variable, e.g.:
```
TEST=1 ./buildall.sh
```

or

```
cd tools/
TEST=1 python3 federation2json my_testdata.json
```

To update a previous .json file, skipping the instance list download from mastodon.xyz:
```
JSON_FILE=data/DescribedInstances.json ./buildall.sh
```

Since you read this README all the way to the end, have a gift:
```
THREADS=50 ./buildall.sh
```
Play nice! Cheers.