
from github import Github, GithubException
from random import randint 

def scrapeRepo(db, repo):
  count = 0
  try:
    for commit in repo.get_commits():
      v = (commit.sha, commit.commit.message.strip())
      if v[1] == u'Initial commit':
        continue
      print v[1]
      db.addCommit(*v)
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

