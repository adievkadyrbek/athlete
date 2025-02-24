from fastapi import HTTPException
from sqlalchemy.orm import Session
from lxml import etree
from math import radians, sin, cos, sqrt, atan2
from decimal import Decimal
from app.models import Activity

def validate_gpx_file(file_content: bytes):
    """Validate if the uploaded file is a valid GPX file."""
    try:
        root = etree.fromstring(file_content)
        if root.tag.lower().endswith("gpx"):
            return True
        else:
            raise ValueError("Invalid GPX format: Root tag is not 'gpx'")
    except etree.ParseError:
        raise ValueError("Invalid GPX file: Failed to parse XML content")

def haversine(lat1, lon1, lat2, lon2):
    """The Haversine formula is a equation used to calculate distances on a sphere"""
    # Radius of the Earth in kilometres
    R = 6371.0
    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def calculate_distance(track_points):
    """Calculate total distance (in kilometres) from GPS points"""
    total_distance = 0.0
    for i in range(1, len(track_points)):
        lat1 = track_points[i - 1]['latitude']
        lon1 = track_points[i - 1]['longitude']
        lat2 = track_points[i]['latitude']
        lon2 = track_points[i]['longitude']
        total_distance += haversine(lat1, lon1, lat2, lon2)
    return total_distance

def calculate_duration(track_points):
    """Calculate duration of an activity (in hours)"""
    if not track_points or len(track_points) < 2:
        return 0.0
    else:
        duration = (track_points[-1]['timestamp'] - track_points[0]['timestamp']).total_seconds() / 3600
        return duration

def calculate_average_speed(distance, duration):
    """Calculate average speed of an activity (in km/h)"""
    if duration == 0.0:
        return 0.0
    else:
        average_speed = distance / duration
        return average_speed

def calculate_elevation_gain(track_points):
    elevation_gain = Decimal('0')
    for i in range(1, len(track_points)):
        elevation_diff = track_points[i]['elevation'] - track_points[i - 1]['elevation']
        if elevation_diff > 0:
            elevation_gain += elevation_diff
    return elevation_gain

def calculate_max_heart_rate(age):
    return 220 - age

def get_heart_rate_zones(max_heart_rate):
    zones = {
        'zone-1': (max_heart_rate * 0.5, max_heart_rate * 0.6),
        'zone-2': (max_heart_rate * 0.6, max_heart_rate * 0.7),
        'zone-3': (max_heart_rate * 0.7, max_heart_rate * 0.8),
        'zone-4': (max_heart_rate * 0.8, max_heart_rate * 0.9),
        'zone-5': (max_heart_rate * 0.9, max_heart_rate)
    }
    return zones

def analyze_heart_rate(heart_rate, zones):
    for zone, (lower, upper) in zones.items():
        if lower <= heart_rate <= upper:
            return zone

def get_heart_rate_zone_counts(track_points, age):
    zone_counts = {
        'zone-1': 0,
        'zone-2': 0,
        'zone-3': 0,
        'zone-4': 0,
        'zone-5': 0,
    }
    max_heart_rate = calculate_max_heart_rate(age)
    zones = get_heart_rate_zones(max_heart_rate)
    for i in range(len(track_points)):
        heart_rate = track_points[i]['heart_rate']
        zone = analyze_heart_rate(heart_rate, zones)
        zone_counts[zone] += 1
    return zone_counts

def list_activities(db: Session):
    """List activity summaries with optional date filtering"""
    try:
        activities = db.query(Activity).all()
        return [activity.to_dict() for activity in activities]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))