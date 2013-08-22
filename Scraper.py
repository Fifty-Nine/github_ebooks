
from github import Github, GithubException
from random import randint 

def filterCommit(message):
  message = message.strip()
  return \
    len(message) > 0 and \
    message.find('Initial commit') < 0 and \
    message.find('Merge pull request') < 0 and \
    not message.startswith('Signed-off-by') and \
    message.find('#') < 0

def scrapeRepo(db, repo):
  count = 0
  try:
    for commit in repo.get_commits():
      sha = commit.sha
      message = commit.commit.message.strip()
      message = ' '.join(filter(filterCommit, message.split('\n')))
      if len(message) > 0:
        print message
        db.addCommit(sha, message)
        count += 1
  except GithubException as e:
    if e.status != 409 or e.message != u'Git Repository is empty.':
      raise e

  return count
    
def scrapeUser(db, user):
  count = 0
  for repo in user.get_repos():
    count += scrapeRepo(db, repo)

  return count

def scrape(db, search):
  gh = Github(db.getConfigValue('api_key'))
  gh.per_page = 10
  
  repos = gh.legacy_search_repos(keyword=search)

  count = 0
  for repo in repos:
    count += scrapeRepo(db, repo)

  return count

