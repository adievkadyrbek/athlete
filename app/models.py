
from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(DateTime, nullable=False)
    total_distance = Column(Float, nullable=False)
    average_speed = Column(Float, nullable=False)
    elevation_gain = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    heart_rate_zones = Column(JSON)

    def to_dict(self):
        return {
            "activity_id": self.activity_id,
            "start_time": self.start_time,
            "total_distance": self.total_distance,
            "average_speed": self.average_speed,
            "elevation_gain": self.elevation_gain,
            "duration": self.duration,
            "heart_rate_zones": self.heart_rate_zones
        }
