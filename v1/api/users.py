from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse,Response

from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema.schemas import Login as SchemaLogin
from model.models import User as ModelUser
from model.models import LastLogin as ModelLastLogin
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


router_user = APIRouter(prefix="/v1/api/user", tags=["/v1/api/user"])

class UserEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ModelUser):
            return {
                'covers': o.covers,
                'fans': o.fans,
                'following': o.following,
                'heart': o.heart,
                'nickname': o.nickname,
                'signature': o.signature,
                'tiktokId': o.tiktokId,
                'uniqueId': o.uniqueId,
                'verified': o.verified,
                'video': o.video,
                'stars':o.stars,
                '_id':str(o._id),
                'isNew':o.isNew,
            }
        return super().default(o)
    

class ProfileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ModelUser):
            return {
                '_id':str(o._id),
                'signature': o.signature,
                'nickname': o.nickname,
                'uniqueId': o.uniqueId,
                'tiktokId': o.tiktokId,
                'verified': o.verified,
                'avatarLarger': o.avatarLarger,
                'fans': o.fans,
                'following': o.following,
                'heart': o.heart,
                'video': o.video,
                'stars':o.stars,
                'isNew':o.isNew,
                'createdAt':format_datetime(o.createdAt),
                'updatedAt':format_datetime(o.updatedAt),
                'covers': o.covers,   
            }
        return super().default(o)


@router_user.post('/login')
async def usere(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    data = json.loads(body)
    username =data.get('username')
    print('Starting get username: {}'.format(username))
    date = datetime.now()
    jsonProfile = tiktok_api_get_profile(username)
    fans = jsonProfile.get('fans')
    heart = jsonProfile.get('heart')
    video = jsonProfile.get('video')
    following = jsonProfile.get('following')
    uniqueId = jsonProfile.get('uniqueId')

    existing_user=db.query(ModelUser).filter_by(uniqueId=username).first()

    if existing_user is not None:
            
            url = existing_user.covers
            if len(url) == 0:
                url = download_avatar(jsonProfile.get('avatarLarger').replace('\\u0026', '&'), username)
            else:
                if existing_user.updatedAt:
                    date_time = existing_user.updatedAt + timedelta(days=3)
                    if date > date_time:
                        url = download_avatar(jsonProfile.get('avatarLarger').replace('\\u0026', '&'), username)
    else:
        url = download_avatar(jsonProfile.get('avatarLarger').replace('\\u0026', '&'), username)
    
    

    if not existing_user:
        jsonProfile['stars'] = 5
        jsonProfile['isNew'] = True
        jsonProfile['createdAt'] = date
        jsonProfile['updatedAt'] = date
        jsonProfile['covers'] = '{}images/{}'.format(API, url)

        db_user = ModelUser(signature= jsonProfile['signature'], nickname=jsonProfile['nickname'], uniqueId=jsonProfile['uniqueId'], 
                            tiktokId=jsonProfile['tiktokId'], verified=jsonProfile['verified'],
                            following=jsonProfile['following'], fans=jsonProfile['fans'], heart=jsonProfile['heart'], 
                            video=jsonProfile['video'], avatarLarger=jsonProfile['avatarLarger'],
                            stars=335, isNew=jsonProfile['isNew'], 
                            covers=jsonProfile['covers'])
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        existing_user.fans=fans
        jsonProfile['stars'] = existing_user.stars
        existing_user.heart=heart
        existing_user.video=video
        existing_user.following=following
        existing_user.isNew=False
        existing_user.updatedAt=datetime.now()

        db.commit()
        db.refresh(existing_user)

    user=db.query(ModelUser).filter_by(uniqueId=uniqueId).first()
    user_json = json.dumps(user, cls=UserEncoder, indent=4)    
    
    user_dict = json.loads(user_json)
    return Response(content=returnProfile(user_dict, db), media_type="application/json")


    

def returnProfile(user, db):
    user_id = user.get('uniqueId')
    db_lastlogin = ModelLastLogin(userId=user_id, lastLogin=datetime.now())
    db.add(db_lastlogin)
    db.commit()
    
    if 'tokens' in user:
        del user['tokens']
    if 'pageProps' in user:
        del user['pageProps']
    if 'avatarLarger' in user:
        del user['avatarLarger']
    
    a = {"data": user, "message": "success", "error": 0}
    a_json = json.dumps(a)  # sözlüğü JSON formatına dönüştür
    return a_json



# @router_user.post('/updateToken')
# async def update_token(request: Request, db: Session = Depends(get_db)):
#     body = await request.body()
#     data = json.loads(body)
#     token = data.get('token')
#     user_id = data.get('userId')
#     existing_user=db.query(ModelUser).filter_by(_id=user_id).first()
    


@router_user.post('/profile')
async def get_profile(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    data = json.loads(body)
    userId = data.get('userId')
    existing_user=db.query(ModelUser).filter_by(_id=userId).first()
    if existing_user is None:
        return Response(content={"message": "something wrong!", "error": 1}, media_type="application/json",status_code=200)
    
    user_json = json.dumps(existing_user, cls=ProfileEncoder, indent=4)    
    
    user_dict = json.loads(user_json)

    #print(user_dict)
    a = {"data": user_dict, "message": "success", "error": 0}
    a_json = json.dumps(a)
    return Response(content=a_json, media_type="application/json")
    #a = {"data": user, "message": "success", "error": 0}
    #a_json = json.dumps(a)  # sözlüğü JSON formatına dönüştür
    #return ok(user)
    # Diğer alanların doğrulamasını yapabilirsiniz

    # İşlemleri gerçekleştirirken hata durumunda HTTPException ile uygun durum kodunu ve hata mesajını döndürebilirsiniz

    # existing_user = db.query(ModelUser).filter_by(nickname=user.nickname).first()
    # if existing_user:
    #     existing_user.avatarLarger = user.avatarLarger
    #     db.commit()
    #     db.refresh(existing_user)
    #     return existing_user
    # else:
    #     db_user = ModelUser(signature=user.signature, nickname=user.nickname, uniqueId=user.uniqueId, tiktokId=user.tiktokId, verified=user.verified,
    #                         following=user.following, fans=user.fans, heart=user.heart, video=user.video, avatarLarger=user.avatarLarger,
    #                         stars=user.stars, isNew=user.isNew, covers=user.covers, hasFollowTiktok=user.hasFollowTiktok, tokens=user.tokens)
    #     db.add(db_user)
    #     db.commit()
    #     db.refresh(db_user)
    #     return db_user

# @router_user.post('/login', response_model=SchemaUser)
# async def user(user: SchemaUser, db: Session = Depends(get_db)):
#     #print(user.signature)
#     db_user = ModelUser(signature=user.signature, nickname=user.nickname, uniqueId=user.uniqueId, tiktokId=user.tiktokId, verified=user.verified,
#                         following=user.following, fans=user.fans, heart=user.heart, video=user.video, avatarLarger=user.avatarLarger,
#                         stars=user.stars, isNew=user.isNew, covers=user.covers, hasFollowTiktok=user.hasFollowTiktok, tokens=user.tokens)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

