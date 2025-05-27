from .. import db

class ProjectType(db.Model):
    __tablename__ = 'project_type'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    resources = db.relationship('Resource', back_populates='project_type')

    def __str__(self):
        return self.name


class Resource(db.Model):
    __tablename__ = 'resource'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    hours_per_unit  = db.Column(db.Float, nullable=False)
    rate_per_hour   = db.Column(db.Float, nullable=False)

    project_type_id = db.Column(db.Integer, db.ForeignKey('project_type.id', ondelete='CASCADE'), nullable=False)
    project_type    = db.relationship('ProjectType', back_populates='resources')
