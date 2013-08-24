import sqlite3
import re

class Database:
  def __init__(self, path='github_ebooks.db'):
    self._conn = sqlite3.connect(path)
    self.evolve()

  @staticmethod
  def _regexp(pattern, data):
    return re.search(pattern, data, re.U) is not None

  def _getCursor(self, cursor=None):
    return cursor if cursor is not None else self._conn.cursor()

  def _commit(self):
    self._conn.commit()

  def evolve(self):
    needs_evolution = False;
    try:
      v = self.getConfigValue('version', int)
      needs_evolution = v is None or (v < 1)
    except sqlite3.OperationalError:
      needs_evolution = True

    self._conn.create_function('regexp', 2, Database._regexp)
    if needs_evolution:
      c = self._getCursor()
      c.execute('''CREATE TABLE Config (
        Key text NOT NULL PRIMARY KEY,
        Value text)''')
      c.execute('''CREATE TABLE Commits (
        Hash text NOT NULL PRIMARY KEY,
        Description text)''')
      self.setConfigValue('version', 1, cursor=c)
      self._commit()

  def setConfigValue(self, key, value, cursor=None):
    c = self._getCursor(cursor)
    c.execute('REPLACE INTO Config (Key, Value) VALUES(?, ?)', (key, value))
    if cursor is not None:
      self._commit()

  def getConfigValue(self, key, parser=str, default=None):
    c = self._getCursor()
    c.execute('SELECT Value FROM Config WHERE Key=?', (key,))
    r = c.fetchone()
    return parser(r[0]) if r is not None else default

  def addCommits(self, commits):
    c = self._getCursor()
    c.executemany('REPLACE INTO Commits VALUES(?, ?)', commits)
    self._commit()

  def addCommit(self, hash_value, text):
    c = self._getCursor()
    c.execute('REPLACE INTO Commits VALUES(?, ?)', (hash_value, text))
    self._commit()

  def allCommits(self):
    c = self._getCursor()
    c.execute('SELECT Hash, Description FROM Commits')
    return c.fetchall()

  def searchCommits(self, search):
    c = self._getCursor()
    c.execute("""
      SELECT Hash, Description FROM Commits 
      WHERE Description REGEXP ?""", (search,))
    return c.fetchall()

  def dropCommits(self, search):
    c = self._getCursor()
    c.execute("""
      DELETE FROM Commits
      WHERE Description REGEXP ?""", (search,))
    self._commit()

  def resetCommits(self):
    c = self._getCursor()
    c.execute('DELETE FROM Commits')
    self._commit()

  def getConfig(self):
    c = self._getCursor()
    c.execute("SELECT Key, Value FROM Config")
    return dict(c.fetchall())

  def setConfig(self, d):
    c = self._getCursor()
    c.executemany("REPLACE INTO Config(Key, Value) VALUES(?, ?)", d.items())
    self._commit()




