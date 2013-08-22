import twitter

class Tweeter:
  def __init__(self, db):
    self.consumer_key = db.getConfigValue('t_api_ck', default='')
    self.consumer_secret = db.getConfigValue('t_api_cs', default='')
    self.access_key = db.getConfigValue('t_api_at', default='')
    self.access_secret = db.getConfigValue('t_api_ats', default='')
    self.db = db

    self.api = None

  def _initApi(self):
    self.api = twitter.Api(
        consumer_key=self.consumer_key, 
        consumer_secret=self.consumer_secret,
        access_token_key=self.access_key,
        access_token_secret=self.access_secret)

  def saveKeys(self):
    self.db.setConfigValue('t_api_ck', self.consumer_key)
    self.db.setConfigValue('t_api_cs', self.consumer_secret)
    self.db.setConfigValue('t_api_at', self.access_key)
    self.db.setConfigValue('t_api_ats', self.access_secret)

  def tweet(self, message):
    if self.api is None:
      self._initApi()
    self.api.PostUpdate(message)

