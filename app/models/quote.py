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
    custom_label     = db.Column(db.String(100), nullable=True)
    quantity         = db.Column(db.Integer, nullable=False, default=1)
    video_seconds    = db.Column(db.Integer, nullable=True)
    video_type_id    = db.Column(db.Integer, db.ForeignKey('video_type.id', ondelete='SET NULL'), nullable=True)

    quote        = db.relationship('Quote', back_populates='items')
    project_type = db.relationship('ProjectType')
    video_type   = db.relationship('VideoType')

    @property
    def unit_cost(self):
        return sum(r.hours_per_unit * r.rate_per_hour for r in self.project_type.resources)

    @property
    def total_cost(self):
        if self.video_type and self.video_seconds:
            return round(self.video_type.cost_per_second * self.video_seconds, 2)

        return round((self.unit_cost / 0.5) * self.quantity, 2)

    @property
    def label(self):
        return self.custom_label or self.project_type.name