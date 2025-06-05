from app import db

class VideoType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    cost_per_second = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<VideoType {self.name} @ ${self.cost_per_second}/sec>"
