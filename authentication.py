from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status
from models import User


load_dotenv()
pwd_contxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

KEY = os.getenv("SECRET")
ALGO = "HS256"


async def token_verify(token: str):
    try:
        data = jwt.decode(token=token, key=KEY, algorithms=ALGO)
        print(f"Decoding {data}")
        user = await User.get(id=data.get("id"))
        # return data["user_id"]
    except JWTError as e:
        print(f"error in token verify {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild Token",
            # headers=b
        )
    return user


def token_encode(data: dict):
    try:
        token = jwt.encode(data, key=KEY, algorithm=ALGO)
        return token
    except Exception as e:
        print(f"Unable to encode {e}")


def hash_password(password) -> str:
    return pwd_contxt.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_contxt.verify(plain_password, hashed_password)
