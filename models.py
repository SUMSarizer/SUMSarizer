import datetime
from app import db

class Datasets(db.Model):
  __tablename__ = 'datasets'

  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.Date, default=datetime.datetime.now)
  title = db.Column(db.Unicode)

  def __init__(self, value):
    self.value = value
    
  def __repr__(self):
    return '<id {}>'.format(self.id)