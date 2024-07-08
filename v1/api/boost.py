from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse,Response

from fastapi_sqlalchemy import DBSessionMiddleware, db


from model.models import User as ModelUser
from model.models import BoostStar,Feeds,HistoryBoost
from fastapi.encoders import jsonable_encoder


from database.session import get_db
from tiktok.tiktok import tiktok_api_get_profile, download_avatar
import json
from datetime import datetime, timedelta,timezone
from config import API

def format_datetime(dt):
    dt_utc = dt.replace(tzinfo=timezone.utc)
    formatted_dt = dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return formatted_dt[:-4] + 'Z'

response_content = {"message": "User not found", "error": 1}
response_contentt = {"message": "something wrong! user is None", "error": 1}
response_content_json = json.dumps(response_content)
response_content_jsonn = json.dumps(response_contentt)

class BoostEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BoostStar):
            return {
                '_id': str(o._id),
                'stars': o.stars,
                'numberOfFollower': o.numberOfFollower,
                'createdAt': format_datetime(o.createdAt),
                'updatedAt': format_datetime(o.updatedAt),
            }
        return super().default(o)
    

router_booster = APIRouter(prefix="/v1/api/feed", tags=["/v1/api/feed"])

@router_booster.post('/getAllBoost')
async def get_all_boost(db: Session = Depends(get_db)):
    
    existing_user=db.query(BoostStar).all()
    user_json = json.dumps(existing_user, cls=BoostEncoder, indent=4)    
    
    user_dict = json.loads(user_json)
    
    a = {"data": user_dict, "message": "success", "error": 0}
    a_json = json.dumps(a)
    return Response(content=a_json, media_type="application/json")

@router_booster.post('/boost')
async def boost(request: Request,db: Session = Depends(get_db)):
    body = await request.body()
    data = json.loads(body)
    stars = data.get('stars')
    boost_star_id = data.get('boostStarsId')
    userId = data.get('userId')
   
    existing_user=db.query(ModelUser).filter_by(_id=userId).first()

    if existing_user is None:
        return Response(content=response_content_jsonn, media_type="application/json",statuscode=400)
    uniqueId = existing_user.uniqueId
    real_star = existing_user.stars
    if real_star < stars:
        return Response(content=response_content_jsonn, media_type="application/json",statuscode=200)

    feed=db.query(Feeds).filter_by(uniqueId=uniqueId).first()
    date = datetime.now()

    # Feed Collection
    if feed is None:
    
        db_feed = Feeds(signature= existing_user.signature, 
                            nickname=existing_user.nickname, 
                            uniqueId=existing_user.uniqueId, 
                            tiktokId=existing_user.tiktokId, verified=existing_user.verified,
                            following=existing_user.following, fans=existing_user.fans, 
                            heart=existing_user.heart, 
                            video=existing_user.video, 
                            avatarLarger=existing_user.avatarLarger,
                            isNew=existing_user.isNew, 
                            createdAt=datetime.now(),
                            updatedAt=datetime.now(),
                            covers=existing_user.covers,
                            hasFollowTiktok=existing_user.hasFollowTiktok,
                            boostStars=stars)
        db.add(db_feed)
        db.commit()
        db.refresh(db_feed)
    else:
        stars += feed.boostStars
        feed_id = feed._id
        feed._id=feed_id
        feed.boostStars=stars
        feed.updatedAt=datetime.now()
        db.commit()
        db.refresh(feed)
        

    # User Collection
    stars_after_used = real_star - data.get('stars')
    print('real_star: {}, stars {}, stars_after_used {}'.format(real_star, stars, stars_after_used))
    existing_user.stars=stars_after_used
    db.commit()
    db.refresh(existing_user)
    
    db_history = HistoryBoost(createdAt= datetime.now(), 
                            updatedAt=datetime.now(), 
                            userId=userId, 
                            profile=uniqueId, boostStars=data.get('stars'),
                            boostStarsId=boost_star_id)
    db.add(db_history)
    db.commit()

    # History Collection
    b = {
        'data': {
            'boost': data.get('stars')
        },
        'message': 'success',
        'error': 0
    }
    b_json = json.dumps(b)
    return Response(content=b_json, media_type="application/json")
