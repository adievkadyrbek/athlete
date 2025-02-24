import os
from fastapi import HTTPException
from celery import Celery
from lxml import etree
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from app.schemas import ActivityModel
from app.models import Activity
from app.database import SessionLocal
from app.helpers import calculate_distance, calculate_duration, calculate_average_speed, calculate_elevation_gain, get_heart_rate_zone_counts

REDIS_URL = os.getenv("REDIS_URL")
celery_app = Celery('project', broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(bind=True, max_retries=3)
def process_gpx_file(self, file_content, user_age):
    db = SessionLocal()
    try:
        tree = etree.fromstring(file_content)
        namespaces = {
            'gpx': 'http://www.topografix.com/GPX/1/1',
            'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
        }

        track_points_list = []
        tracks = tree.findall('gpx:trk', namespaces)
        for track in tracks:
            segments = track.findall('gpx:trkseg', namespaces)
            for segment in segments:
                track_points = segment.findall('gpx:trkpt', namespaces)
                for track_point in track_points:
                    latitude = track_point.get('lat')
                    longitude = track_point.get('lon')
                    elevation = track_point.find('gpx:ele', namespaces).text
                    timestamp = track_point.find('gpx:time', namespaces).text
                    heart_rate = track_point.find('.//gpxtpx:hr', namespaces).text
                    track_point_data = {
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'),
                        'latitude': Decimal(str(latitude)),
                        'longitude': Decimal(str(longitude)),
                        'elevation': Decimal(str(elevation)),
                        'heart_rate': Decimal(int(heart_rate)),
                    }
                    track_points_list.append(track_point_data)

        total_distance = calculate_distance(track_points_list)
        duration = calculate_duration(track_points_list)
        average_speed = calculate_average_speed(total_distance, duration)
        elevation_gain = calculate_elevation_gain(track_points_list)
        heart_rate_zones = get_heart_rate_zone_counts(track_points_list, user_age)

        activity_data = {
            'activity_id': self.request.id,
            'start_time': track_points_list[0]['timestamp'].isoformat(),
            'total_distance': Decimal(str(total_distance)),
            'average_speed': Decimal(str(average_speed)),
            'elevation_gain': Decimal(str(elevation_gain)),
            'duration': Decimal(str(duration)),
            'heart_rate_zones': heart_rate_zones
        }

        response = create_activity(ActivityModel(**activity_data), db)
        return response
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

def create_activity(activity: ActivityModel, db: Session):
    try:
        activity_object = Activity(
            activity_id=activity.activity_id,
            start_time=activity.start_time,
            total_distance=activity.total_distance,
            average_speed=activity.average_speed,
            elevation_gain=activity.elevation_gain,
            duration=activity.duration,
            heart_rate_zones=activity.heart_rate_zones
        )

        db.add(activity_object)
        db.commit()
        db.refresh(activity_object)

        return {
            "message": "Activity created successfully",
            "activity_id": activity.activity_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))