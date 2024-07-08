# build a schema using pydantic
from pydantic import BaseModel

class Login(BaseModel):
    
    username : str
    imei : str
    model : str
    manufacturer : str
    bundleId : str
    versionCode : str
    versionName : str

    class Config:
        orm_mode = True




class User(BaseModel):
    
    signature : str
    nickname : str
    uniqueId : str
    tiktokId : str
    verified : bool
    following : int
    fans : int
    heart : int
    video : int
    avatarLarger : str
    stars :int
    isNew : bool
    covers : str
    hasFollowTiktok : bool
    tokens : str

    class Config:
        orm_mode = True

class Tracking(BaseModel):
    userId: str
    imei : str
    screenDisplayId : str
    model : str
    manufacturer : str
    osCodename : str
    osVersion : str
    product : str
    hardware : str
    displayVersion : str
    bundleId : str
    versionCode : str
    versionName : str
    packageName : str
    hash : str
    time : str
    contentType : str
    http_user_agent  : str
    http_host : str
    http_accept_encoding : str
    remote_port : int
    class Config:
        orm_mode = True