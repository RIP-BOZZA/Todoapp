from fastapi import APIRouter ,Depends ,HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext # password hasing
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm ,OAuth2PasswordBearer
from datetime import timedelta ,datetime ,timezone
from jose import jwt ,JWTError


router=APIRouter(
    prefix='/auth',
    tags=['auth']# tag will divde apis in to tags and other
)

SECRET_KEY= "15d61f1b856b30e8918aed96fe4e8e590de2ac4ba6e37f562202f7a7653e27f3"
ALGORITHAM= "HS256" # secret key and algoritham makes secure token ,signature

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally :
        db.close()

db_dependancy =Annotated[Session,Depends(get_db)] # dependancy injection



# intitlaizing a cryptcontext
bcrypt_context =CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer =OAuth2PasswordBearer(tokenUrl="auth/token") # tokenUrl="token" this url client sent to fastapi  ,this will check in jwt header for token is came from which api

class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    role:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str


@router.post("/create_user" ,status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependancy ,create_user:CreateUserRequest ):
    create_user_model = Users(
        email =create_user.email,
        username=create_user.username,
        first_name = create_user.first_name,
        last_name = create_user.last_name,
        role=create_user.role,
        # hashed_password = create_user.password
        # this will hash the password
        hashed_password = bcrypt_context.hash(create_user.password)

    )
    db.add(create_user_model)
    db.commit()
    return create_user_model


def autheticate_user(username:str ,password:str ,db):
    user = db.query(Users).filter(Users.username==username).first()
    if user is None:
        return False
    #verify secret against an existing hash ,check passwords match
    if not bcrypt_context.verify(password ,user.hashed_password):
        return False

    return user


def create_access_token(username:str ,user_id:int ,expires_delta:timedelta):
    """create a jwt access token with username ,id,and expiration time"""
    encode = {"sub":username ,"id":user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode ,SECRET_KEY,algorithm=ALGORITHAM)


async def get_current_user(token:Annotated[str ,Depends(OAuth2PasswordBearer)]):
    """
    function to set validate all bearer token in header
    """
    try:
        payload =jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHAM])
        username:str =payload.get('sub')
        user_id :int = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,detail="could not valid user")
        return {"username":username ,"id":user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,detail="could not valid user")


@router.post("/token" ,response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm ,Depends()],
                                 db:db_dependancy):
    user= autheticate_user(form_data.username ,form_data.password ,db)
    if not user :
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,detail="could not valid user")
    # set 20 minite expiration time
    token = create_access_token(user.username,user.id,timedelta(minutes=20))
    return {
        "access_token":token ,"token_type":"bearer"
    }