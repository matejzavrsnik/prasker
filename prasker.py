import urllib.request
import urllib.error
import urllib.parse
import os.path
import codecs
import argparse
import sys
import hashlib
import re
import signal
from collections import deque
from time import sleep, gmtime, strftime
from bs4 import BeautifulSoup

#todo: http://360percents.com/wordlist/

def current_date_time():
	result = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	return result

def print_raw(*text):  
	rawout = open(1, "w", encoding="utf8", closefd=False)  
	print(*text, file=rawout)  
	rawout.flush()  
	rawout.close()

def append_to_file(filename,text):
	if filename is None or filename == "":
		return
	file = codecs.open(filename, "a", "utf8")
	file.write("{0}\n".format(text))
	file.close()
	
def verbose_print (verbosity_set,verbosity_msg,file,text):
	text = current_date_time() + ": " + text
	if verbosity_msg <= verbosity_set:
		print_raw(text)
		append_to_file(file,text)
	
class class_trace:
	trace_file = ""
	verbose_level = False
	def set_trace(self, file, verbose):
		self.trace_file = file
		self.verbose_level = verbose
	
def timeout_handler(signum, frame):
	raise Exception("Timeout!")

def starts_with_any_of(string, prefixes):
	for prefix in prefixes:
		if string.startswith(prefix):
			return True
	return False
	
class class_dictionary(class_trace):
	words = set() # collection of dictionary words
	not_words = set() # collection of new words, that were not found in dictionary
	name = "" # name of dictionary: filename from dictionary file. 
	file_notindictionary = "" # to which file, if any, should be stored words, that are not in dictionary
	ignore_dic = None
	words_indictionary = 0 # counter of words, that were found in dictionary in checking last text
	words_total = 0 # counter of all the words from last text check
	def __init__(self,dictionary,notdictionary,ignore):
		if dictionary is None or dictionary == "":
			return
		if os.path.isfile(dictionary):
			with open(dictionary, "r", encoding="utf8") as f:
				for word in f:
					self.words.add(word.lower().strip())
			f.close()
			self.name = os.path.basename(dictionary)
		# where to note the words that haven't been found in dictionary
		self.file_notindictionary = notdictionary
		# which words to ommit from the list of words not found in dictionary
		if not ignore is None and not ignore is "":
			self.ignore_dic = class_dictionary(ignore,None,None)
	def is_in(self,word):
		clean_word = re.sub("[\W:\.]+", " ", word)
		clean_word = clean_word.lower().strip()
		# it is "in" when it is found in dictionary. Numeric values are valid in all languages
		# so numbers are automatically "in" without dictionary check
		if len(clean_word) > 0 and (clean_word in self.words or clean_word.isnumeric()):
			return True
		elif len(clean_word) > 0:
			# store unique words that are not in the dictionary to separate file, they might be suitable for adding them to dictionary
			# ignore words from the other dictionary, the "ignore dictionary", if it exists
			if clean_word not in self.not_words and (self.ignore_dic is None or not self.ignore_dic.is_in(clean_word)):
				append_to_file(self.file_notindictionary,clean_word)
				self.not_words.add(clean_word)
			verbose_print (self.verbose_level,3,self.trace_file,"Not in dictionary: {0}".format(clean_word))
		return False
	def percent_in(self,text):
		words_in_text = re.split("[\W\s:\.]+",text)
		self.words_indictionary = 0
		self.words_total = len(words_in_text)
		for word in words_in_text:
			if self.is_in(word):
				self.words_indictionary = self.words_indictionary + 1
		result = self.words_indictionary / self.words_total
		return result
	def count_words_indictionary(self):
		return self.words_indictionary
	def count_words_total(self):
		return self.words_total
	def is_initialized(self):
		if len(self.words) > 0:
			return True
		else:
			return False

class class_urlstorage(class_trace):
	visited = set()
	unvisited = deque() # using queue: first added links to be processed first 
	allowed_domains = set()
	# todo: add another limit to adding url: links deep level
	maxurlbuffer = 10000
	trace_file = ""
	verbose_level = False
	def set_trace(self, file, verbose):
		self.trace_file = file
		self.verbose_level = verbose
	def store (self,url,from_url):
		url = self.fix_url (url,from_url)
		if (len(url) > 0) and (url not in self.visited) and (url not in self.unvisited):
			#possibility: and not on ignore list: youtube, twitter (blacklist)
			
			# max size of url buffer, since every page has more then 1 link on average, this set would otherwise only grow
			# only add if from specified domain, ignore the rest (whitelist)
			# todo: how do I break a line in two in python?
			if (not len(self.unvisited) > self.maxurlbuffer) and (len(self.allowed_domains) == 0 or starts_with_any_of(url, self.allowed_domains)): 
				self.unvisited.append(url)
				return True
			else:
				return False
		else:
			return False
	def fix_url (self,parsed_url,page_url):
		fixed_url = ""
		# skip urls that start with javascript, # or mailto, they are of no use
		if isinstance(parsed_url, str) and not parsed_url.startswith("javascript") and not parsed_url.startswith("#") and not parsed_url.startswith("mailto"):
			parsed_url_parts = list(urllib.parse.urlparse(parsed_url)) # break url into parts
			page_url_obj = urllib.parse.urlparse(page_url) # break an originating url into parts
			# id url is missing information where it is needed, replace that information with parts of url from the originating page
			# this is supposed to fix "\r\programming" into "http://www.reddit.com/r/programming" for instance
			if not isinstance(parsed_url_parts[0], str) or len(parsed_url_parts[0])==0: # http:// part
				if len(page_url_obj.scheme)==0:
					parsed_url_parts[0] = "http://"
				else:
					parsed_url_parts[0] = page_url_obj.scheme
			if not isinstance(parsed_url_parts[1], str) or len(parsed_url_parts[1])==0: # www.reddit.com part
				parsed_url_parts[1] = page_url_obj.netloc
			fixed_url = urllib.parse.urlunparse(parsed_url_parts) # assemble mixed information back together
		# remove whitespace chars from url (\s option -> [ \t\n\r\f\v]
		fixed_url = re.sub("\s+", "", fixed_url)
		return fixed_url
	def next (self):
		# retrieve next unvisited url
		if not self.empty ():
			next_url = self.unvisited.popleft() # get some url from collection of unvisited
			self.visited.add(next_url) # this one is now considered visited
			return next_url
	def empty (self):
		if len(self.unvisited) > 0:
			return False
		else:
			return True
	def size (self):
		return len(self.unvisited)

class class_textstorage(class_trace):
	stored_text_hashes = set() # a collection of hashes of texts that have been stored already
	new_texts_stored = 0
	new_duplicate_texts = 0
	percent_dictionary = 0
	words_indictionary_aggregate = 0
	words_total_aggregate = 0
	text_html_tags = ["p","a","em","strong","div","blockquote","span","small","dt","td","dd","font","h1","h2","h3","h5","h6","b","i","u"]
	unwanted_html_tags = ["script","style"]
	trace_file = ""
	verbose_level = False
	def set_trace(self, file, verbose):
		self.trace_file = file
		self.verbose_level = verbose
	def write_to_file (self,soup,element,tofile,dictionary):
		for el in soup.find_all(element):
			top_element = el
			# climb to the highest text element in html structure. for instance, <b> tag enclosed in <p> should
			# not be read separately, just as the parent <p> tag content should not miss the content of <b>
			while not (top_element.parent is None) and not (top_element.parent.name is None) and (top_element.parent.name in self.text_html_tags):
				top_element = top_element.parent
			string_element = str(top_element.get_text())
			string_element = self.fix_text(string_element) # remove unwanted chars
			string_element = string_element.strip()
			if len(string_element) > 10:
				hash = hashlib.sha224(string_element.encode("utf-8")).hexdigest()
				if not hash in self.stored_text_hashes:
					verbose_print (self.verbose_level,3,self.trace_file,"Hash check done. This is new text. Hash: {0} Text: {1}".format(hash,string_element))
					self.stored_text_hashes.add(hash) #just hash, not string. strings might get big
					# 80% of words should be from the dictionary language
					self.percent_dictionary = 1.0
					if dictionary.is_initialized():
						self.percent_dictionary = dictionary.percent_in(string_element)
					if self.percent_dictionary > 0.8:
						append_to_file(tofile,"{0}".format(string_element))
						self.new_texts_stored = self.new_texts_stored + 1
						verbose_print (self.verbose_level,3,self.trace_file,"Accepted. Percent in dictionary: {0}".format(self.percent_dictionary))
					else:
						verbose_print (self.verbose_level,3,self.trace_file,"Not accepted. Percent in dictionary: {0} Text: {1}".format(self.percent_dictionary,string_element))
						pass
					# pick up words statistics
					#todo: convert all increments to += style
					self.words_indictionary_aggregate += dictionary.count_words_indictionary()
					self.words_total_aggregate += dictionary.count_words_total()
				else:
					self.new_duplicate_texts = self.new_duplicate_texts + 1
					# verbose_print (self.verbose_level,3,self.trace_file,"Text already seen, not storing. Hash: {0}".format(hash))
	def extract_text (self,soup,tofile,dictionary):
		self.new_texts_stored = 0 # reset counters for tracing purposes
		self.new_duplicate_texts = 0
		self.words_indictionary_aggregate = 0
		self.words_total_aggregate = 0
		self.remove_unwanted(soup) # remove unwanted tags
		for tag in self.text_html_tags: # store every text from specified elements to file
			self.write_to_file (soup,tag,tofile,dictionary)
	def remove_unwanted (self,soup):
		# remove unwanted tags like <style> and <script> from parsing.
		# they contain text, but not such that would be visible in web browser
		# but first, add space to begining and end of texts, 
		# so that they are still separated when HTML tags are removed and fused later
		for tag in soup.find_all():
			if not tag.string is None:
				tag.string = " " + tag.string + " "
		for unwanted in self.unwanted_html_tags:
			for tag in soup.find_all(unwanted):
				tag.decompose()
	def fix_text (self,text):
		# remove residual html tags
		text = re.sub("<.+>", "", text)
		# remove web links from text (you want to keep them? then comment out)
		text = re.sub("https?:\/\/[^ ]+", "", text)
		# remove all unwanted chars from middle of text
		# with \s it replaces [ \t\n\r\f\v] and other whitespace characters with single space
		# this is for repeated tabs or spaces, a common pattern in HTML pages
		text = re.sub("\s+", " ", text)
		return text
	def count_new_texts_stored (self):
		return self.new_texts_stored
	def count_new_duplicate_texts (self):
		return self.new_duplicate_texts
	def count_words_indictionary(self):
		return self.words_indictionary_aggregate
	def count_words_total(self):
		return self.words_total_aggregate
	def count_texts_stored (self):
		return len(self.stored_text_hashes)

def main():
	# idea: an option to resume: flush all hashes, settings, everything to file and when given the resume file, start from there
	global doc # documentation and instructions
	parser = argparse.ArgumentParser(description="This is a script for parsing visible text from web pages.")
	parser.add_argument("-u", "--url", required=True, help="Single starting url or a text file with starting collection of urls.")
	parser.add_argument("-o", "--output", required=True, help="Filename where you would like to get scraped text.")
	parser.add_argument("-t", "--trace", help="Filename where you would like to get trace information.")
	parser.add_argument("-a", "--domains", help="A list of comma separated domains allowed for scraping. If empy, no restrictions.")
	parser.add_argument("-d", "--dictionary", help="Dictionary file containing words of the desired language.")
	parser.add_argument("-v", "--verbose", type=int, default=1, help="increase output verbosity (default: 1)")
	parser.add_argument("-s", "--wordstore", help="where should words that are not in dictionary be stored")
	parser.add_argument("-i", "--ignoredic", help="list of words, that shouldn't go on not-in-dictionary list, even when not found in dictionary")
	# todo: add links deep option
	parser.add_argument("-w", "--wait", type=int, default=5, help="timeout between subsequent url requests (default: 5)")
	parser.add_argument("-b", "--maxurlbuffer", type=int, default=10000, help="max size of unvisited url buffer (default: 10000)")
	args = parser.parse_args()
	
	# typical uses
	# prasker.py --url [http://www.reddit.com | urllist.txt] --output output.txt
	# prasker.py --url urls.txt --output output.txt --trace trace.txt --dictionary slo.dic --ignoredic eng.dic --wordstore newwords.txt --wait 5 --maxurlbuffer 20000 --verbose 1
	# prasker.py --url https://www.bbc.co.uk/ --output bbc_news --trace trace_news --domains https://www.bbc.co.uk/news,http://www.bbc.co.uk/news
		
	# initialize dictionaries
	dictionary = class_dictionary(args.dictionary,args.wordstore,args.ignoredic)
	dictionary.set_trace(args.trace,args.verbose)
		
	# initialize url buffer and add starter pack
	urls = class_urlstorage()
	urls.set_trace(args.trace,args.verbose)
	urls.maxurlbuffer = args.maxurlbuffer
	urls.allowed_domains = args.domains.split(",")
	if not args.url is None and os.path.isfile(args.url):
		with open(args.url, "r") as f:
			for urlline in f:
				urls.store(urlline,"")
		f.close()
	elif not args.url is None:
		urls.store(args.url,"")
	else:
		return

	# initialize text storage object for storing parsed text and keeping track of already stored items
	textstorage = class_textstorage()
	textstorage.set_trace(args.trace,args.verbose)
	
	# assemble filename with embeded dictionary name
	output_filename = args.output
	if dictionary.name != "":
		output_filename = dictionary.name + "_" + output_filename

	# go
	# pretend you're normal browser. some sites block scripts. wikipedia, for instance
	agent_headers = { "User-Agent" : "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11" }
	megabyte = 1024*1024*10
	while( not urls.empty() ):
		url = urls.next()
		verbose_print (args.verbose,1,args.trace,"In {0}s will open url: {1}".format(args.wait,url))
		sleep(args.wait) # wait a while: a lot of repeated requests might cause some servers to deny access
		# about sleep: good to know, speed is not the issue here :)
		try: # if 1 == 1: # 
			# create request with fake User-Agent
			page_request = urllib.request.Request(url, headers=agent_headers)
			# set the timer: allow maximum of 60 seconds for opening url.
			# some pages will hang opening process for too long, skip those.
			# in case of timeout, just let main try catch it and move on to next url
			page = urllib.request.urlopen(page_request, timeout=60) # open page
			new_links = 0
			# to prevent streaming media like http://mp3.rtvslo.si/val202
			contentType = page.getheader("Content-Type")	
			if contentType.startswith("text/html"):
				# if you're on *nix you can set up timeout even on opening a page. Useful on some veeery slow pages
				# like http://blog.thc.org/index.php?/archives/1-GSM-Researcher-stopped-at-Heathrow-Airport-by-UK-government-officials.html
				if os.name == "posix":
					signal.signal(signal.SIGALRM, timeout_handler)
					signal.alarm(60)   # Ten seconds
				# parse html document, read at most 10MB of html data. More than that is likely an error
				soup = BeautifulSoup(page.read(megabyte))
				if os.name == "posix":
					signal.alarm(0)
				textstorage.extract_text (soup,output_filename,dictionary)  # extract visible text from web page
				new_texts = textstorage.count_new_texts_stored() # solely for tracing purposes
				total_texts = textstorage.count_texts_stored()
				duplicate_texts = textstorage.count_new_duplicate_texts()
				not_in_dictionary_percent = 1
				if textstorage.count_words_total() > 0: # avoid division by zero
					not_in_dictionary_percent = textstorage.count_words_indictionary() / textstorage.count_words_total()
				not_in_dictionary_words = textstorage.count_words_total() - textstorage.count_words_indictionary()
				verbose_print (args.verbose,1,args.trace,"Added {0} new text blocks, filtered {1} duplicates, words not in this language: {2} of {3}. New total: {4}".format(new_texts,duplicate_texts,not_in_dictionary_words,textstorage.count_words_total(),total_texts))
				if not_in_dictionary_percent > 0.8: # if not more then 80% of words are in this language, ignore links from here
					for link in soup.find_all("a"): # find all links to other web pages
						new_url = link.get("href")
						# store web link for visiting later
						# originating web page is needed to fix incomplete links, like "\media\list.html"
						# see function doc for details
						stored = urls.store(new_url,url)
						if stored:
							new_links = new_links + 1 # solely for tracing purposes
					if new_links > 0:
						verbose_print (args.verbose,1,args.trace,"Added {0} new links. New total: {1}".format(new_links,urls.size())) # solely for tracing purposes
				else:
					verbose_print (args.verbose,1,args.trace,"Skipped links on this page. Percent of words in this language: {0}".format(not_in_dictionary_percent))
			else:
				verbose_print (args.verbose,1,args.trace,"Skipped {0} content on: {1}".format(contentType,url))
		except:
			verbose_print (args.verbose,1,args.trace,"Error scraping page: {0}".format(url))

if __name__ == "__main__":
	main()
