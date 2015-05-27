import datetime
from app import db
from dateutil.parser import parse as date_parse


class StudyUsers(db.Model):
    __tablename__ = 'study_users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), index=True)
    role = db.Column(db.Enum('labeller', 'owner', name='user_role'))

    def __init__(self, user_id, study_id, role):
        self.study_id = study_id
        self.user_id = user_id
        self.study_id = study_id
        self.role = role


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    stormpath_id = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    study_roles = db.relationship('StudyUsers',
                                  backref=db.backref('users'), lazy='dynamic')

    labels = db.relationship('UserLabels',
                             backref='users', lazy='dynamic')

    def __init__(self, stormpath_user):
        self.stormpath_id = stormpath_user.get_id()
        self.email = stormpath_user.email

    @classmethod
    def from_stormpath(cls, stormpath_user):
        return Users.query.filter_by(stormpath_id=stormpath_user.get_id()).first()

    def studies(self):
        return db.session.query(Studies, StudyUsers).\
            join(StudyUsers).filter_by(user_id=self.id)


class StudyUploads(db.Model):
    __tablename__ = 'study_uploads'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    filename = db.Column(db.Unicode)
    data = db.Column(db.LargeBinary)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), index=True)

    def __init__(self, filename, data, study_id):
        self.filename = filename
        self.data = data
        self.study_id = study_id


class Studies(db.Model):
    __tablename__ = 'studies'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    title = db.Column(db.Unicode)

    datasets = db.relationship('Datasets', lazy="dynamic", cascade="all, delete-orphan", backref="study")
    uploads = db.relationship('StudyUploads', lazy="dynamic", cascade="all, delete-orphan", backref="study")

    users = db.relationship('StudyUsers',
                            backref=db.backref('studies'), lazy='dynamic')

    def __init__(self, title):
        self.title = title

    def add_user(self, user, role):
        study_user = StudyUsers(user.id, self.id, role)
        self.users.append(study_user)
        db.session.commit()

    def get_roles(self, user):
        roles = [study_user.role for study_user in self.users.filter_by(user_id=user.id).all()]
        return roles

    def is_labeller(self, user):
        return ("labeller" in self.get_roles(user)) or ("owner" in self.get_roles(user))

    def is_owner(self, user):
        return "owner" in self.get_roles(user)

    def delete(self):
        for dataset in self.datasets:
            dataset.delete()
        self.uploads.delete()
        db.session.delete(self)
        db.session.commit()

    def labellers(self):
        return Users.query.join(StudyUsers).\
            filter(StudyUsers.role == "labeller").\
            filter(StudyUsers.study_id == self.id)


class Datasets(db.Model):
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    title = db.Column(db.Unicode)
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'), index=True)

    notes = db.relationship('Notes', cascade="all, delete-orphan", backref="dataset", lazy="dynamic")
    user_labels = db.relationship('UserLabels', cascade="all, delete-orphan", backref="dataset", lazy="dynamic")
    data_points = db.relationship('DataPoints', cascade="all, delete-orphan", backref="dataset", lazy="dynamic")
    labelled = db.relationship('LabelledDatasets', cascade="all, delete-orphan", backref="dataset", lazy="dynamic")

    def __init__(self, title, study_id, notes=[], data_points=[]):
        self.title = title
        self.study_id = study_id
        self.notes = notes
        self.data_points = data_points

    def next(self):
        return Datasets.query.\
            filter(Datasets.study_id == self.study_id).\
            filter(Datasets.created_at < self.created_at).\
            order_by(Datasets.created_at.desc()).\
            first()

    def prev(self):
        return Datasets.query.\
            filter(Datasets.study_id == self.study_id).\
            filter(Datasets.created_at > self.created_at).\
            order_by(Datasets.created_at).\
            first()

    def items(self):
        return Datasets.query.\
            filter(Datasets.study_id == self.study_id).\
            order_by(Datasets.created_at.desc()).\
            all()

    def labels_for_user(self, user):
        return db.session.query(Datasets, DataPoints, UserLabels).\
            filter_by(id=self.id).\
            join(UserLabels).filter_by(user_id=user.id).\
            join(DataPoints).\
            order_by(DataPoints.timestamp)

    def delete(self):
        self.user_labels.delete()
        self.notes.delete()
        self.data_points.delete()
        self.labelled.delete()
        db.session.delete(self)
        db.session.commit()

    def user_has_labelled(self, user):
        return self.labelled.filter_by(user_id=user.id).count() > 0


class LabelledDatasets(db.Model):
    __tablename__ = 'labelled_datasets'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    def __init__(self, dataset_id, user_id):
        self.dataset_id = dataset_id
        self.user_id = user_id


class Notes(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    text = db.Column(db.Unicode)

    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), index=True)

    def __init__(self, text):
        self.text = text

    @classmethod
    def dict_from_parsed(cls, text, dataset_id):
        return dict(
            created_at=datetime.datetime.now(),
            text=text,
            dataset_id=dataset_id
        )


class DataPoints(db.Model):
    __tablename__ = 'datapoints'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    timestamp = db.Column(db.DateTime, index=True)
    unit = db.Column(db.String(16))
    value = db.Column(db.Float)
    # Add Boolean training set column
    training = db.Column(db.Boolean)

    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), index=True)
    user_labels = db.relationship('UserLabels', backref="datapoint", lazy="dynamic", passive_deletes=True)

    def __init__(self, timestamp, unit, value):
        self.timestamp = timestamp
        self.unit = unit
        self.value = value

    @classmethod
    def dict_from_parsed(cls, parsed_point, dataset_id, training_selector):
        timestamp = date_parse(parsed_point[0])
        return dict(
            created_at=datetime.datetime.now(),
            timestamp=timestamp,
            unit=parsed_point[1],
            value=float(parsed_point[2]),
            dataset_id=dataset_id,
            training=training_selector(timestamp)
        )


class UserLabels(db.Model):
    __tablename__ = 'user_labels'

    id = db.Column(db.Integer, primary_key=True)
    datapoint_id = db.Column(db.Integer, db.ForeignKey('datapoints.id'), index=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    label = db.Column(db.Boolean)

    def __init__(self, datapoint_id, dataset_id, user_id, label=False):
        self.datapoint_id = datapoint_id
        self.dataset_id = dataset_id
        self.user_id = user_id
        self.label = False

    @classmethod
    def dicts_from_datapoints(cls, data_points, dataset_id, user_id):
        dicts = [dict(datapoint_id=data_point.id,
                      dataset_id=dataset_id,
                      user_id=user_id,
                      label=False) for data_point in data_points]
        return dicts
