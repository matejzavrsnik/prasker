####
Prasker
####
Prasker 1.0
10-Feb-2012

Prasker is a command line python script, that parses visible text from html pages and continues on pages they link to, forever.

************
Installation
************

Currently it doesn't install. It is used directly from console.

There is a trick though. At the time of writing the script, BeautifulSoup 4.1.3 (august 20., 2012) had problems with python 3.2, so the modified version of it was included in the folder itself. (I don't remember where I got the fixed version from, probably some Git repo...) It should work without problem in later revisions of the library, but you should adjust the import clause on the top of script. Currently it's set so that it loads the library from bs4 subfolder. The lazy way is to copy the library in bs4 subfolder, as stated in BeautifulSoup doc, that's it.

**********
ChangeLogs
**********

This is the first version.

************
Requirements
************

* Python 3.2
* BeautifulSoup 4.1.3

****************************
Getting Started with Prasker
****************************

Simple:

* prasker.py -url http://www.reddit.com --output output.txt

Parse the page at www.reddit.com and all links on it. Then follow links and repeat. Output scraped text in output.txt file.

Like, advanced:

* prasker.py --url urls.txt --output output.txt --trace trace.txt --dictionary slo.dic --ignoredic eng.dic --wordstore newwords.txt --wait 5 --maxurlbuffer 20000 --verbose 1

Parse the urls that are listed in urls.txt file, fifo order. Store only texts that are written in language, whose words are stored in slo.dic (text file, a word per line). Output parsed text in slo.dic_output.txt (prepended with dictionary filename). Store trace messages to trace.txt.  Store new words in file newwords.txt, unless they are found in "ignore dictionary" eng.dic. Between each request, wait 5 seconds, to avoid banning. Do not keep more that 20000 urls in buffer. Set verbose level to 1.

********
Features
********

* Loading a list of starting urls from file
* Inserting url from command line argument
* Skips pages who's Content-Type is not text/html (streaming media, xml, ...)
* Fakes Mozilla user agent
* Adjustable wait between subsequent requests to avoid ban
* Times out if page loads too slowly and proceeds
* An error in parsing page does not stop the parser
* Limits the size of HTML page to 10MB, after that it stops receiving
* Parses links from pages and visits them too, in fifo order
* Ajdustable buffer size for url queue
* If parsed links are incomplete, it tries to fix them first
* Saves scraped text to specified file
* Filters already seen blocks of text
* Utf-8 compatible
* Adjustable verbose level
* Trace messages can be saved to separate file
* Language aware scraping
  * Only scrapes desired language (a collection of words in separate file must be passed to script)
  * Links on pages, which are not writte in desired language, are not visited
  * Unknown words from pages, written in desired language, can be stored in separate file
  * Unless they are already present in another seperate file, called "ignore dictionary", then it doesn't save them

### Language aware scraping

Prasker does not only scrape pages, it can differentiate amongst different languages. For this to work, user must pass the script a file in which all, or majority of the words in a langage are stored. Each block of text on the page is then scanned, each word is compared to the dictionary file. If 80% of words are found in dictionary, it is considered, that the page is written in that language. The rest of the words are unknown, but can be stored in separate file for later reviewing, maybe adding to the main dictionary in subsequent runs, or just collecting new words or whatever. If new word is not found in main dictionary, it is also looked for in "ignore dictionary", if the script was given such a file. If such word is found in "ignore dictionary" it is then not added to new words collection. Output text at the end is prepended with dictionary filename to avoid confusion on multiple subsequent runs.

### Dictionaries

Some Slovenian and English dictionaries can be found on unaffiliated http://360percents.com/wordlist/

*********
Copyright
*********

Prasker Copyright (c) 2013 Matej Zavrsnik <matejzavrsnik@gmail.com> (matejzavrsnik.com)

Prasker is distributed under MIT licence as stated on http://opensource.org/licenses/MIT
See LICENCE file for details.

Copyright of suggested site for dictionaries and dictionaries themselves is unknown. The publisher of the site is Konstantin Kovshenin.
Python Copyright (c) 1990-2013, Python Software Foundation
BeautifulSoup and Crummy (c) 1996-2013 Leonard Richardson