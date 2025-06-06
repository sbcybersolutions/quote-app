from .quote import Quote, QuoteItem
from .resource import ProjectType, Resource
from .video_type import VideoType  # ✅ Register VideoType

__all__ = [
    "Quote",
    "QuoteItem",
    "ProjectType",
    "Resource",
    "VideoType"  # ✅ Include in __all__ for full exposure
]
