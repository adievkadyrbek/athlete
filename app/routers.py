from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ActivityModel
from app.models import Activity
from app.tasks import process_gpx_file
from app.helpers import list_activities, validate_gpx_file

router = APIRouter()

@router.post("/activities/upload")
async def upload_activity(file: UploadFile = File(...), user_age: int = 27):
    """Upload and process GPX file"""
    try:
        if not file.filename.lower().endswith(".gpx"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only GPX files are allowed.")
        file_content = await file.read()
        try:
            validate_gpx_file(file_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        task = process_gpx_file.delay(file_content, user_age)
        return {"task_id": task.id, "message": "Activity processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/{activity_id}", response_model=ActivityModel)
async def get_activity(activity_id: str, db: Session = Depends(get_db)):
    """Retrieve activity data"""
    try:
        activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity: {str(e)}")

@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get aggregated statistics"""
    try:
        activities = list_activities(db)
        stats = {
            'total_activities': len(activities),
            'total_distance': sum(activity['total_distance'] for activity in activities),
            'total_duration': sum(activity['duration'] for activity in activities),
            'average_speed': sum(activity['average_speed'] for activity in activities) / len(activities) if activities else 0,
            'total_elevation_gain': sum(activity['elevation_gain'] for activity in activities)
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))