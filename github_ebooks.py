#!/usr/bin/python
import sys
import argparse
import codecs

from Database import Database
from Markov import SequenceGenerator

def readFromFile(path, db):
  f = codecs.open(path, 'r', 'utf-8')

  commits = []
  for line in f:
    line = line.strip()
    commits.append((hash(line), line))

  db.addCommits(commits)

def printCommits(db):
  for (hash, msg) in db.allCommits():
    print msg

def generate(db):
  sg = SequenceGenerator(1)
  for commit in db.allCommits():
    sg.addSample(commit[1].split(' '))

  print ' '.join(sg.generate())


def main(argv):
  parser = argparse.ArgumentParser(description='github_ebooks')
  parser.add_argument('--api-key', dest='api_key',
      help='Set the API key used for scraping commits')
  parser.add_argument('--commit-file', dest='commit_file', 
      help='Read commits from the given file and save them in the database')
  parser.add_argument('--print-commits', dest='print_commits', 
      action='store_const', const=True, default=False)
  parser.add_argument('--generate', dest='generate', 
      action='store_const', const=True, default=False)
  args = parser.parse_args(argv[1:])

  db = Database()

  if args.api_key is not None:
    db.setConfigValue('api_key', args.api_key)

  if args.commit_file is not None:
    readFromFile(args.commit_file, db)

  if args.print_commits:
    printCommits(db)

  if args.generate:
    generate(db)

  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))

