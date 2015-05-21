import datetime
from app import db
import sumsparser as parser
from dateutil.parser import parse as date_parse
    
study_users = db.Table('study_users',
    db.Column('study_id', db.Integer, db.ForeignKey('studies.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Users(db.Model):
  __tablename__ = 'users'
  
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Unicode)
  email = db.Column(db.Unicode)
  studies = db.relationship('Studies', secondary=study_users,
        backref=db.backref('users', lazy='dynamic'))
  
  def __init__(self, user):
    self.user_id = user.get_id()
    self.email = user.email
    
  @classmethod
  def fromStormpath(cls,user):
    print user.get_id()
    return Users.query.filter_by(user_id=user.get_id()).first()

class Studies(db.Model):
  __tablename__ = 'studies'
  
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=datetime.datetime.now)
  title = db.Column(db.Unicode)
  owner = db.Column(db.Unicode)
  
  datasets = db.relationship('Datasets', lazy="dynamic", backref="study")
  
  #users = db.relationship('Users', secondary=study_users,
  #      backref=db.backref('studies', lazy='dynamic'))
  
  def __init__(self, title, owner):
    self.title = title
    self.owner = owner.get_id()
    
  def authorizedUser(self,user):
    return (self.users.filter_by(user_id=user.get_id()).count()>0)

class Datasets(db.Model):
  __tablename__ = 'datasets'

  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=datetime.datetime.now)
  title = db.Column(db.Unicode)
  labelled = db.Column(db.Boolean)
  
  notes = db.relationship('Notes')
  data_points = db.relationship('DataPoints', order_by="DataPoints.timestamp", backref="dataset",lazy="dynamic")
  
  study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))

  def __init__(self, title, study, notes = [], data_points = []):
    self.title = title
    self.study_id = study.id
    self.notes = notes
    self.data_points = data_points
  
  @classmethod
  def from_file(cls, file, filename, study):
    parsed = parser.parse(file)
    
    notes = [Notes(note_text) for note_text in parsed['notes']]
    data_points=[DataPoints.from_parsed(parsed_point) for parsed_point in parsed['data']]
    dataset = Datasets(filename, study, notes, data_points)
    return dataset
    
  def next(self):
    return Datasets.query\
      .filter(Datasets.study_id==self.study_id)\
      .filter(Datasets.created_at < self.created_at)\
      .order_by(Datasets.created_at.desc())\
      .first()
        
  def prev(self):
    return Datasets.query\
      .filter(Datasets.study_id==self.study_id)\
      .filter(Datasets.created_at > self.created_at)\
      .order_by(Datasets.created_at)\
      .first()

  def items(self):
    return Datasets.query\
      .filter(Datasets.study_id==self.study_id)\
      .order_by(Datasets.created_at.desc())\
      .all()

class Notes(db.Model):
  __tablename__ = 'notes'
  
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=datetime.datetime.now)
  text = db.Column(db.Unicode)
  
  dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
  
  def __init__(self, text):
    self.text = text

class DataPoints(db.Model):
  __tablename__ = 'datapoints'
  
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime, default=datetime.datetime.now)
  timestamp = db.Column(db.DateTime)
  unit = db.Column(db.String(16))
  value = db.Column(db.Float)
  selected = db.Column(db.Boolean)
  # Add Boolean training set column
  training = db.Column(db.Boolean)
  
  dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'))
  
  def __init__(self, timestamp, unit, value):
    self.timestamp = timestamp
    self.unit = unit
    self.value = value
    
  @classmethod
  def from_parsed(cls, parsed_point):
    return DataPoints(date_parse(parsed_point[0]),
                              parsed_point[1],
                              float(parsed_point[2]))
