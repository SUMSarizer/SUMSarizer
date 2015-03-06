import datetime
from app import db

class Datasets(db.Model):
  __tablename__ = 'datasets'

  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.Date, default=datetime.datetime.now)
  title = db.Column(db.Unicode)
  
  notes = db.relationship('Notes')

  def __init__(self, title):
    self.title = title
  
  @classmethod
  def from_file(cls, file):
    import sumsparser as parser
    parsed = parser.parse(file)
    dataset = Datasets(file.filename)
    for note_text in parsed['notes']:
      note = Notes(note_text)
      dataset.notes.append(note)
    return dataset
    
  def __repr__(self):
    return '<id {}>'.format(self.id)

class Notes(db.Model):
  __tablename__ = 'notes'
  
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.Date, default=datetime.datetime.now)
  text = db.Column(db.Unicode)
  
  dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
  
  def __init__(self, text):
    self.text = text

class DataPoints(db.Model):
  __tablename__ = 'datapoints'
  
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.Date, default=datetime.datetime.now)
  timestamp = db.Column(db.Date)
  unit = db.Column(db.String(16))
  value = db.Column(db.Float)
  
  def __init__(self, timestamp, unit, value):
    self.timestamp = timestamp
    self.unit = unit
    self.value = value