# Described Instance List README
This folder contains python tools to download information on every instance in the Mastodon federation and generate documents with this information.

| Script | Effect | output file |
|--------|--------|--------|
|tools/federation2json.py | downloads and generates .json database | data/DescribedInstances.json |
|tools/json2markdown.py | generates a markdown file from the .json database, above | data/DescribedInstances.md |
|tools/markdown2html.sh | generates an HTML file from .md file, above (requires "markdown" command) | data/DescribedInstances.html |
|tools/json2sqlite.py | generates an sqlite database of the .json file, above | data/DescribedInstances.sqlite |
|buildall.sh | generates all of the above | data/* |

### Warning
These tools are *ad hoc kludges* to get the job done only. I'm not interested in developing a syncronizing system that can update records, resume downloads, merge data, guess schema, etc. etc. This is a one-shot tool that you can run for 30 minutes to get all the info you wish.

### Dependencies
Python 3, and also:
```
pip3 install bs4      # BeautifulSoup, for parsing HTML
pip3 install requests # for downloading websites without complex syntactic junk
```
You also need the `markdown` command in your $PATH if you wish to generate html. I use [discount](http://www.pell.portland.or.us/~orc/Code/discount/).

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
. markdown2html.sh ../data/DescribedInstances.md ../data/DescribedInstances.html
python3 json2sqlite.py ../data/DescribedInstances.json ../data/DescribedInstances.sqlite
```

This is pretty much what the `build.sh` script does.

### Tinkering
If you want to test a smaller set of random instance data, set the `TEST=1` environment variable, e.g.:
```
TEST=1 ./buildall.sh
```

```
cd tools/
TEST=1 python3 federation2json my_testdata.json
```
