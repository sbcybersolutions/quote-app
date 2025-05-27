from datetime import datetime
from .. import db

class Quote(db.Model):
    __tablename__ = 'quote'
    id            = db.Column(db.Integer, primary_key=True)
    client_name   = db.Column(db.String(100), nullable=False)
    project_name  = db.Column(db.String(100), nullable=False)
    project_date  = db.Column(db.Date, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('QuoteItem', back_populates='quote', cascade='all, delete-orphan')


class QuoteItem(db.Model):
    __tablename__ = 'quote_item'
    id               = db.Column(db.Integer, primary_key=True)
    quote_id         = db.Column(db.Integer, db.ForeignKey('quote.id', ondelete='CASCADE'), nullable=False)
    project_type_id  = db.Column(db.Integer, db.ForeignKey('project_type.id', ondelete='RESTRICT'), nullable=False)
    quantity         = db.Column(db.Integer, nullable=False, default=1)

    quote        = db.relationship('Quote', back_populates='items')
    project_type = db.relationship('ProjectType')

    @property
    def unit_cost(self):
        return sum(r.hours_per_unit * r.rate_per_hour for r in self.project_type.resources)

    @property
    def total_cost(self):
        return self.unit_cost * self.quantity
