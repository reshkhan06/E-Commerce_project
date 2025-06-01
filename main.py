from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from util import UPLOAD_DIR
from fastapi.staticfiles import StaticFiles

from routes.user import router as user_routes
from routes.product import router as product_routes
from routes.bussiness import router as bussiness_routes


app = FastAPI()

# Tortoise ORM DB setup
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

# Mounting static
app.mount("/files", StaticFiles(directory=UPLOAD_DIR))

# All Router Here
app.include_router(user_routes, prefix="/user")
app.include_router(product_routes, prefix="/product")
app.include_router(bussiness_routes, prefix="/business")


# Root Route
@app.get("/")
def index():
    return {"message": "Hello, welcome to E-commerce!"}
