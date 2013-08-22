
from github import Github, GithubException
from random import randint 

class Scraper:
  def __init__(self, db):
    self.db = db

    api_key = db.getConfigValue('api_key')
    self.gh = Github(api_key)
    self.gh.per_page = 10

  def _filterCommit(self, message):
    message = message.strip()
    return \
      len(message) > 0 and \
      message.find('Initial commit') < 0 and \
      message.find('Merge pull request') < 0 and \
      not message.startswith('Signed-off-by') and \
      message.find('#') < 0

  def scrapeRepo(self, repo_name):
    return self._scrapeRepo(self.gh.get_repo(repo_name))

  def _scrapeRepo(self, repo):
    count = 0
    try:
      for commit in repo.get_commits():
        sha = commit.sha
        message = commit.commit.message.strip()
        message = ' '.join(filter(self._filterCommit, message.split('\n')))
        if len(message) > 0:
          print message
          self.db.addCommit(sha, message)
          count += 1
    except GithubException as e:
      if e.status != 409 or e.message != u'Git Repository is empty.':
        raise e

    return count

  def scrapeUser(self, user_name):
    return self._scrapeUser(self.gh.get_user(user_name))

  def _scrapeUser(self, user):
    count = 0
    for repo in user.get_repos():
      count += self._scrapeRepo(repo)

    return count

  def scrape(self, search):
    repos = self.gh.legacy_search_repos(keyword=search)
    count = 0
    for repo in repos:
      count += self._scrapeRepo(repo)

    return count

