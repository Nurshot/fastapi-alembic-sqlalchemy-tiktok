from sqlalchemy import Column, Integer, String, Boolean,Date, ForeignKey,JSON,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base  = declarative_base()

class User(Base):
    __tablename__ = 'users'
    _id  = Column(Integer, primary_key=True, index=True)
    signature = Column(String,nullable=True)
    nickname = Column(String)
    uniqueId = Column(String)
    tiktokId = Column(String)
    verified = Column(Boolean)
    following = Column(Integer)
    fans = Column(Integer)
    heart = Column(Integer)
    video = Column(Integer)
    avatarLarger = Column(String)
    stars = Column(Integer)
    isNew = Column(Boolean)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    covers = Column(String)
    hasFollowTiktok = Column(Boolean,nullable=True)
    tokens = Column(String,nullable=True)



class Tracking(Base):
    __tablename__ = 'trackings'
    _id  = Column(Integer, primary_key=True, index=True)
    userId= Column(String)
    imei = Column(String)
    screenDisplayId = Column(String)
    model = Column(String)
    manufacturer = Column(String)
    osCodename = Column(String)
    osVersion = Column(String)
    product = Column(String)
    hardware = Column(String)
    displayVersion = Column(String)
    bundleId = Column(String)
    versionCode = Column(String)
    versionName = Column(String)
    packageName = Column(String)
    hash = Column(String)
    time = Column(String)
    contentType = Column(String)
    http_user_agent = Column(String)
    http_host = Column(String)
    http_accept_encoding = Column(String)
    remote_port = Column(Integer)
    createdAt = Column(DateTime(timezone=True))


class LastLogin(Base):
    __tablename__ = 'last-login'
    _id  = Column(Integer, primary_key=True, index=True)
    userId = Column(String)
    lastLogin = Column(DateTime)


class Ads(Base):
    __tablename__ = 'ads'
    
    _id  = Column(Integer, primary_key=True, index=True)
    configType = Column(String,default="ads")
    adsType = Column(String)
    adsName = Column(String)
    adsId = Column(String)
    enable = Column(Boolean)

class BoostPackage(Base):
    __tablename__ = 'boost-package'
    
    _id  = Column(Integer, primary_key=True, index=True)
    packageId = Column(String)
    os = Column(String)
    packageName = Column(String)
    packageStar = Column(Integer)
    pricing = Column(Integer)

class BoostStar(Base):
    __tablename__ = 'boost-star'
    
    _id  = Column(Integer, primary_key=True, index=True)
    stars = Column(Integer)
    numberOfFollower = Column(Integer)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class HistoryFollow(Base):
    __tablename__ = 'history-follow'
    
    _id  = Column(Integer, primary_key=True, index=True)
    feedId = Column(String)
    userId = Column(String)
    createdAt = Column(DateTime)
    
class HistoryBoost(Base):
    __tablename__ = 'history-boost'
    
    _id  = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    userId = Column(String)
    profile = Column(String)
    boostStars=Column(Integer)
    boostStarsId=Column(String)

class Feeds(Base):
    __tablename__ = 'feeds'
    
    _id  = Column(Integer, primary_key=True, index=True)
    feedid=Column(String,nullable=True)
    signature = Column(String,nullable=True)
    nickname = Column(String)
    uniqueId = Column(String)
    tiktokId = Column(String)
    verified = Column(Boolean)
    following = Column(Integer)
    fans = Column(Integer)
    heart = Column(Integer)
    video = Column(Integer)
    avatarLarger = Column(String)
    isNew = Column(Boolean)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    covers = Column(String)
    hasFollowTiktok = Column(Boolean,nullable=True)
    boostStars=Column(Integer)

 