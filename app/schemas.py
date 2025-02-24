from pydantic import BaseModel
from datetime import datetime

class ActivityModel(BaseModel):
    activity_id: str
    start_time: datetime
    total_distance: float
    average_speed: float
    elevation_gain: float
    duration: float
    heart_rate_zones: dict