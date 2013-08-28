#!/usr/bin/python
import sys
import argparse
import codecs
import re
import string
from random import choice, randint, paretovariate
from itertools import chain

from github_ebooks import Database, SequenceGenerator, Scraper, Tweeter

whitespace_re = re.compile(r'\s', re.U)
punct_re = re.compile(r'(.+)([\?\.!;])+', re.U)

# A list of names. These are based on the most popular baby names in the US
# in 1987 (best year). There's about an equal number of male/female names, 
# which is not statistically accurate but I'd like to think these nonsensical
# commits are from a future where computing has more gender diversity!
names = [ "Mike", "Jessica", "Chris", "Ashley", "Matt", "Amanda", "Josh",
          "Jenny", "David", "Sarah", "Andrew", "Steph", "Dan", "Brittany",
          "Jim", "Nicole", "Justin", "Heather", "Bob", "Liz", "John", "Sam",
          "Joe", "Meg", "Ryan", "Melissa", "Brandon", "Danny", "Bill", 
          "Amber", "Nick", "Lauren", "Tony", "Rachel", "Jon", "Tiffany", 
          "Kevin", "Emily", "Brian", "Tina", "Tim", "Ben" ]

def randomName(word=""):
  return choice(names)

def randomVersion(word=""):
  source = range(randint(2, 4))
  rand = lambda i: randint(0, (i + 1) * 4)
  return '.'.join([str(rand(i)) for i in source])

replacementTable = (
    ( re.compile(r'@upperName', re.U | re.I), lambda w: randomName().upper() ),
    ( re.compile(r'@name', re.U | re.I),      randomName                     ),
    ( re.compile(r'@version', re.U | re.I),   randomVersion                  )
)

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
    word = word.strip()
    strip = word.rstrip if word.startswith('@') else word.strip
    word = strip(string.punctuation)

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

  result = u' '.join(sequence)

  for (regex, subst) in replacementTable:
    result = regex.sub(lambda match: subst(match.group(0)), result)

  return result

def generate(db, seed=""):
  sg = SequenceGenerator(1)
  for commit in db.allCommits():
    sg.addSamples(tokenify(commit[1]))

  left = list(chain(*tokenify(seed)))

  while True:
    right = list(sg.generate(left))

    words = list(chain(left, right))
    result = fixup(words)
    if len(words) >= 3 and len(result) <= 140:
      return result

def main(argv):
  parser = argparse.ArgumentParser(description='github_ebooks')
  parser.add_argument('--db', default='github_ebooks.db')
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
  parser.add_argument('--find')
  parser.add_argument('--replace')
  parser.add_argument('--reset-commits', action='store_true')
  parser.add_argument('--drop-commits')
  parser.add_argument('--generate', action='store_true')
  parser.add_argument('--seed')
  parser.add_argument('--scrape-search')
  parser.add_argument('--scrape-repo')
  parser.add_argument('--scrape-user')
  parser.add_argument('--tweet', action='store_true')
  args = parser.parse_args(argv[1:])

  db = Database(path=args.db)
  t = Tweeter(db)

  if args.api_key:
    db.saveConfigValue('api_key', args.api_key)

  twitter_keys_changed = False
  if args.twitter_access_token_key:
    t.access_key = args.twitter_access_token_key
    twitter_keys_changed = True
  
  if args.twitter_access_token_secret:
    t.access_secret = args.twitter_access_token_secret
    twitter_keys_changed = True

  if args.twitter_consumer_key:
    t.consumer_key = args.twitter_consumer_key
    twitter_keys_changed = True

  if args.twitter_consumer_secret:
    t.consumer_secret = args.twitter_consumer_secret
    twitter_keys_changed = True

  if twitter_keys_changed:
    t.saveKeys()

  if args.add_commit:
    db.addCommit(hash(args.add_commit), args.add_commit)

  if args.commit_file:
    readFromFile(args.commit_file, db)

  if args.show_keys:
    print 'GitHub: ' + db.getConfigValue('api_key', default='')
    print 'Twitter Consumer Key: ' + t.consumer_key
    print 'Twitter Consumer Secret: ' + t.consumer_secret
    print 'Twitter Access Token Key: ' + t.access_key
    print 'Twitter Access Token Secret: ' + t.access_secret

  if args.print_commits:
    printCommits(db.allCommits())
  
  if not args.find and args.replace:
    pass
  elif args.find and args.replace:
    printCommits(db.subCommits(args.find, args.replace))
  elif args.find:
    printCommits(db.searchCommits(args.find))

  if args.generate:
    print generate(db)

  if args.seed:
    print generate(db, args.seed)

  if args.tweet:
    message = generate(db)
    print message 
    t.tweet(message)
  
  if args.reset_commits:
    db.resetCommits()

  if args.drop_commits:
    db.dropCommits(args.drop_commits)

  sc = Scraper(db)
  if args.scrape_search:
    sc.scrape(args.scrape_search)

  if args.scrape_user:
    sc.scrapeUser(args.scrape_user)

  if args.scrape_repo:
    sc.scrapeRepo(args.scrape_repo)

  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))

