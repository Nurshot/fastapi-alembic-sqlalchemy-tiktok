from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse,Response

from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy import and_, not_, desc

from schema.schemas import Login as SchemaLogin
from model.models import User as ModelUser
from model.models import Feeds,HistoryFollow
from fastapi.encoders import jsonable_encoder


from database.session import get_db
from tiktok.tiktok import tiktok_api_get_profile, download_avatar
import json
from datetime import datetime, timedelta,timezone
from config import API
kUser_Not_Found = "User not found"

router_explore = APIRouter(prefix="/v1/api/feeds", tags=["/v1/api/feeds"])

@router_explore.post('/get')
async def feeds(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    data = json.loads(body)
    
    page_num = data.get('page')
    page_size = data.get('size')
    userId = data.get('userId')
    skips = page_size * (page_num - 1)

    # QUERY HISTORY FIRST
    if len(userId) > 0:
        # QUERY USER TO GET UNIQUEID
        user=db.query(ModelUser).filter_by(_id=userId).first()
        if user is None:
            Response(content={"message": "User not found", "error": 1}, media_type="application/json",status_code=200)
        histories = [userId]
        history_follow = db.query(HistoryFollow).filter_by(_id=userId).all()
        for history in history_follow:
            histories.append(history.feedId)

        feeds = db.query(Feeds).filter(
            Feeds.covers.isnot(None),
            ~Feeds._id.in_(histories),
            Feeds.uniqueId != user.uniqueId
        ).order_by(
            desc(Feeds.boostStars),
            desc(Feeds._id)
        ).offset(skips).limit(page_size).all()

        response_data = []
        for feed in feeds:
            feed_data = {
                'nickname': feed.nickname,
                'uniqueId': feed.uniqueId,
                'signature': feed.signature,
                '_id': feed._id,
                'covers': feed.covers
            }
            response_data.append(feed_data)

        a = {"data": response_data, "message": "success", "error": 0}
        print(a)
        a_json = json.dumps(a)
        return Response(content=a_json, media_type="application/json")
    
response_content = {"message": "User not found", "error": 1}
response_contentt = {"message": "Tiktok Not Found", "error": 1}
response_content_json = json.dumps(response_content)
response_content_jsonn = json.dumps(response_contentt)

@router_explore.post('/follow')
async def follow(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    data = json.loads(body)
    user_id = data.get('userId')
    feed_id = data.get('feedId')
    user=db.query(ModelUser).filter_by(_id=user_id).first()
    if user is None:
        return Response(content=response_content_json, media_type="application/json",status_code=400)
    if user.fans <= 0:
        return Response(content=response_content_json, media_type="application/json",status_code=400)
    feed= db.query(Feeds).filter_by(feedid=feed_id).first()
    if feed is None:
        return Response(content=response_content_json, media_type="application/json",status_code=400)
    if not user.uniqueId:
        return Response(content=response_content_json, media_type="application/json",status_code=400)
    try:
        # check if user following

        tiktok = tiktok_api_get_profile(user.get('uniqueId'))

        tiktok_fans = tiktok.get('following')
        user_fans = user.get('following')

        if tiktok_fans > user_fans:
            # Remove 1 booster
            if feed.boostStars > 0:
                boost_stars = feed.boostStars
                if boost_stars > 0:
                    boost_stars -= 1
                    feed.boostStars=boost_stars
                    feed.updatedAt=datetime.now()
                    db.commit()
                    db.refresh(feed)

            # Give 1 stars reward for user
            stars = user.stars
            stars += 1
            user.stars=stars
            user.following = tiktok_fans
            db.commit()
            db.refresh(user)

            # CHECK IF HISTORY IS EXIST
            
            db_history = HistoryFollow(feedId= feed_id ,userId=user_id,createdAt= datetime.now())
            db.add(db_history)
            db.commit()
            
            a = {"message": "success", "error": 1}
            a_json = json.dumps(a)
            return Response(content=a_json, media_type="application/json")
        else:
            a = {"message": "success", "error": 0}
            a_json = json.dumps(a)
            return Response(content=a_json, media_type="application/json")
    except:
        return Response(content=response_content_jsonn, media_type="application/json",status_code=200)