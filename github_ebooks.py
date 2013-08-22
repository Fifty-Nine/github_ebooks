#!/usr/bin/python
import sys
import argparse
import codecs
import re
import string

from Database import Database
from Markov import SequenceGenerator
from Scraper import Scraper

whitespace_re = re.compile(r'\s', re.UNICODE)
punct_re = re.compile(r'(.+)([\?\.!;])+', re.UNICODE)

def readFromFile(path, db):
  f = codecs.open(path, 'r', 'utf-8')

  commits = []
  for line in f:
    line = line.strip()
    commits.append((hash(line), line))

  db.addCommits(commits)

def printCommits(commits):
  for (hash, msg) in commits:
    print msg.encode('utf-8')

def tokenify(paragraph):
  words = whitespace_re.split(paragraph)
  result = []
  line = []

  for word in words:
    match = punct_re.match(word)
    word = word.strip(string.punctuation + string.whitespace)

    if len(word) > 0:
      line.append(word)

    if word.istitle():
      word = word.lower()

    if match:
      result.append(line)
      line = []
  
  if len(line) > 0:
    result.append(line)

  return result

def fixup(sequence):
  if len(sequence) > 0 and not sequence[0].isupper():
    sequence[0] = sequence[0].capitalize()

  return sequence

def generate(db):
  sg = SequenceGenerator(1)
  for commit in db.allCommits():
    sg.addSamples(tokenify(commit[1]))

  print ' '.join(fixup(list(sg.generate())))

def maybeSaveValue(db, key, value):
  if value is not None:
    db.setConfigValue(key, value)

def main(argv):
  parser = argparse.ArgumentParser(description='github_ebooks')
  parser.add_argument('--api-key', 
      help='Set the API key used for scraping commits')
  parser.add_argument('--add-commit')
  parser.add_argument('--commit-file', 
      help='Read commits from the given file and save them in the database')
  parser.add_argument('--show-keys', action='store_true')
  parser.add_argument('--twitter-consumer-key')
  parser.add_argument('--twitter-consumer-secret')
  parser.add_argument('--twitter-access-token-key')
  parser.add_argument('--twitter-access-token-secret')
  parser.add_argument('--print-commits', action='store_true')
  parser.add_argument('--search-commits')
  parser.add_argument('--reset-commits', action='store_true')
  parser.add_argument('--drop-commits')
  parser.add_argument('--generate', action='store_true')
  parser.add_argument('--scrape-search')
  parser.add_argument('--scrape-repo')
  parser.add_argument('--scrape-user')
  args = parser.parse_args(argv[1:])

  db = Database()

  maybeSaveValue(db, 'api_key', args.api_key)
  maybeSaveValue(db, 'twitter_access_token_key', args.twitter_access_token_key)
  maybeSaveValue(db, 'twitter_access_token_secret', args.twitter_access_token_secret)
  maybeSaveValue(db, 'twitter_consumer_key', args.twitter_consumer_key)
  maybeSaveValue(db, 'twitter_consumer_secret', args.twitter_consumer_secret)

  if args.add_commit is not None:
    db.addCommit(hash(args.add_commit), args.add_commit)

  if args.commit_file is not None:
    readFromFile(args.commit_file, db)

  if args.show_keys:
    print 'GitHub: ' + db.getConfigValue('api_key', default='')
    print 'Twitter Consumer Key: ' + db.getConfigValue('twitter_consumer_key', default='')
    print 'Twitter Consumer Secret: ' + db.getConfigValue('twitter_consumer_secret', default='')
    print 'Twitter Access Token Key: ' + db.getConfigValue('twitter_access_token_key', default='')
    print 'Twitter Access Token Secret: ' + db.getConfigValue('twitter_access_token_secret', default='')

  if args.print_commits:
    printCommits(db.allCommits())

  if args.search_commits is not None:
    printCommits(db.searchCommits(args.search_commits))

  if args.generate:
    generate(db)
  
  if args.reset_commits:
    db.resetCommits()

  if args.drop_commits is not None:
    db.dropCommits(args.drop_commits)

  sc = Scraper(db)
  if args.scrape_search is not None:
    sc.scrape(args.scrape_search)

  if args.scrape_user is not None:
    sc.scrapeUser(args.scrape_user)

  if args.scrape_repo is not None:
    sc.scrapeRepo(args.scrape_repo)


  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))

