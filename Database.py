import sqlite3

class Database:
  def __init__(self):
    self.conn = sqlite3.connect('github_ebooks.db')
    self.c = self.conn.cursor()
    self.evolve()

  def evolve(self):
    needs_evolution = False;
    try:
      v = self.getConfigValue('version', int)
      needs_evolution = v is None or (v < 1)
    except sqlite3.OperationalError:
      needs_evolution = True

    if needs_evolution:
      self.c.execute('''CREATE TABLE Config (
        Key text NOT NULL PRIMARY KEY,
        Value text)''')
      self.c.execute('''CREATE TABLE Commits (
        Hash text NOT NULL PRIMARY KEY,
        Description text)''')
      self.setConfigValue('version', 1)
      self.conn.commit()

  def setConfigValue(self, key, value):
    c = self.conn.cursor()
    self.c.execute('REPLACE INTO Config (Key, Value) VALUES(?, ?)', (key, value))
    self.conn.commit()

  def getConfigValue(self, key, parser=str):
    c = self.conn.cursor()
    self.c.execute('SELECT Value FROM Config WHERE Key=?', (key,))
    r = self.c.fetchone()
    return parser(r[0]) if r is not None else None

  def addCommits(self, commits):
    self.c.executemany('REPLACE INTO Commits VALUES(?, ?)', commits)
    self.conn.commit()

  def addCommit(self, hash_value, text):
    self.c.execute('REPLACE INTO Commits VALUES(?, ?)', (hash_value, text))
    self.conn.commit()

  def allCommits(self):
    self.c.execute('SELECT Hash, Description FROM Commits')
    return self.c.fetchall()

  def resetCommits(self):
    self.c.execute('DELETE FROM Commits')
    self.conn.commit()

