from fastapi import FastAPI, HTTPException, status, Depends, Request
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import *
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mail import send_email, EmailSchema

app = FastAPI()

# Tortoise ORM DB setup
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


# Signal: Auto-create a Business after a User is created
@post_save(User)
async def create_bussiness(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str],
) -> None:
    if created:
        b_obj = await Bussiness.create(b_name=instance.name, owner=instance)
        await Bussiness_Pydantic.from_tortoise_orm(b_obj)


# User Registration Route
@app.post("/registration")
async def user_registration(user: UserIn_Pydantic):

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


@app.put("/reset")
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


@app.get("/verification", response_class=HTMLResponse)
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


@app.post("/login")
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
    return {"message": f"Login sucessfuly {user.name}", "token": token}


# Root Route
@app.get("/")
def index():
    return {"message": "Hello, welcome to E-commerce!"}
