from . import db
from datetime import datetime

class ProjectType(db.Model):
    __tablename__ = 'project_type'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # backref from Resource: project_type.resources
    resources = db.relationship('Resource', back_populates='project_type')


class Resource(db.Model):
    __tablename__ = 'resource'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    hours_per_unit  = db.Column(db.Float, nullable=False)
    rate_per_hour   = db.Column(db.Float, nullable=False)

    project_type_id = db.Column(
        db.Integer,
        db.ForeignKey('project_type.id', ondelete='CASCADE'),
        nullable=False
    )
    project_type = db.relationship(
        'ProjectType',
        back_populates='resources'
    )


class QuoteItem(db.Model):
    __tablename__ = 'quote_item'
    id               = db.Column(db.Integer, primary_key=True)
    quote_id         = db.Column(
        db.Integer,
        db.ForeignKey('quote.id', ondelete='CASCADE'),
        nullable=False
    )
    project_type_id  = db.Column(
        db.Integer,
        db.ForeignKey('project_type.id', ondelete='RESTRICT'),
        nullable=False
    )
    quantity         = db.Column(db.Integer, nullable=False, default=1)

    # relationships
    quote        = db.relationship('Quote', back_populates='items')
    project_type = db.relationship('ProjectType')

    @property
    def unit_cost(self):
        """Sum of (hours_per_unit × rate_per_hour) across all resources."""
        return sum(r.hours_per_unit * r.rate_per_hour for r in self.project_type.resources)

    @property
    def total_cost(self):
        """unit_cost × quantity."""
        return self.unit_cost * self.quantity


class Quote(db.Model):
    __tablename__ = 'quote'
    id            = db.Column(db.Integer, primary_key=True)
    client_name   = db.Column(db.String(100), nullable=False)
    project_name  = db.Column(db.String(100), nullable=False)
    project_date  = db.Column(db.Date, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # backref from QuoteItem: quote.items
    items = db.relationship('QuoteItem', back_populates='quote', cascade='all, delete-orphan')

