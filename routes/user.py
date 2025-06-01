from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi.security import OAuth2PasswordRequestForm

from models import *

from authentication import *
from mail import *


router = APIRouter()


# User Registration Route
@router.post("/registration")
async def user_registration(user: UserIn_Pydantic):

    found_user = await User.get_or_none(email=user.email)

    if found_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User found do login"
        )

    user_info = user.dict(exclude_unset=True)
    user_info["password"] = hash_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await User_Pydantic.from_tortoise_orm(user_obj)

    # send email
    data = {
        "subject": "user register",
        "email": [f"{new_user.email}"],
    }
    email_data = EmailSchema(**data)
    await send_email(email=email_data, instance=new_user)

    return {
        "message": f"Hello {new_user.name}, please check your email inbox for a confirmation link."
    }


@router.put("/reset")
async def reset_pass(data: Reset):
    user = await User.get_or_none(email=data.email)
    print(user)
    if not user:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    new_pass = hash_password(password=data.password)
    user.password = new_pass
    await user.save()
    return {"message": "password has been reset"}


templates = Jinja2Templates(directory="templates")


@router.get("/verification", response_class=HTMLResponse)
async def email_verification(req: Request, token: str):
    user = await token_verify(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse(
            "verification.html", {"request": req, "user_name": user.name}
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invaild Token",
        # headers=b
    )


@router.post("/login")
async def login(data: User_login):
    user = await User.get_or_none(email=data.email)
    if not user:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    if not verify_password(plain_password=data.password, hashed_password=user.password):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password incorrect"
        )

    encode_data = {"id": user.id}

    token = token_encode(encode_data)
    print(token)
    return {"message": f"Login sucessfuly {user.name}", "token": token}


@router.post("/get-token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm provides `username` and `password`
    user = await User.get_or_none(email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    token_data = {"id": user.id}
    token = token_encode(token_data)

    return {"access_token": token, "token_type": "bearer"}
