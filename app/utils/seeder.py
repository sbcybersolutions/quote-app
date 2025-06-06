from app import db
from app.models import VideoType

def seed_video_types():
    if not VideoType.query.first():
        video_types = [
            ("Explainer Video", 20.00),
            ("Promo Video", 25.00),
            ("Internal Training", 18.00),
            ("Product Walkthrough", 22.00),
            ("Compliance Video", 17.00),
            ("Bespoke Course Video", 30.00),
            ("Animated Overview", 28.00),
        ]
        for name, rate in video_types:
            db.session.add(VideoType(name=name, cost_per_second=rate)) # type: ignore
        db.session.commit()
