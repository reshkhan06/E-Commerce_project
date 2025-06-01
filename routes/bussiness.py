from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from models import Bussiness, BussinessIn_Pydantic, User, Update_City
from authentication import get_user
from util import des

router = APIRouter()


@router.post("/")
async def create(
    b_name: str = Form(...),
    city: str = Form(...),
    region: str = Form(...),
    description: str = Form(...),
    logo: UploadFile = File(...),
    user: User = Depends(get_user),
):
    found = await Bussiness.get_or_none(b_name=b_name)
    if found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="business name already exits"
        )

    # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = des / f"{b_name}_{logo.filename}"
    content = await logo.read()
    with open(file_path, "wb") as f:
        f.write(content)

    bussiness = {
        "b_name": b_name,
        "city": city,
        "region": region,
        "description": description,
        "logo": file_path,
        "owner": user,
    }

    data = await Bussiness.create(**bussiness)
    await BussinessIn_Pydantic.from_tortoise_orm(data)
    return {"message": f"Bussiness is created {data.id}"}


# TODO
# get  Busniess account by b_name
# delete Business account by b_nam
# Update  Business account by b_nams , optional parameter
@router.get("/all_bussiness")
async def get_all_business():
    try:
        bus = await Bussiness.all()
        return bus
    except Exception as e:
        print(e)


@router.get("/bussinesss_name")
async def get_business(b_name: str):
    try:
        name = await Bussiness.get_or_none(b_name=b_name)
        return name
    except HTTPException as e:
        raise HTTPException(status_code=404, detail="Business name not found")


@router.patch("/logo")
async def update_logo(b_name: str, logo: UploadFile = File(...)):
    business = await Bussiness.get_or_none(b_name=b_name)
    if not business:
        raise HTTPException(status_code=404, detail="Business name not found")

    file_path = des / f"{b_name}_{logo.filename}"
    content = await logo.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # updation
    business.logo = file_path
    await business.save()
    return {"message": "Logo has been updated"}


@router.patch("/city")
async def update_city(data: Update_City):
    print(data)
    business = await Bussiness.get_or_none(b_name=data.b_name)
    if not business:
        raise HTTPException(status_code=404, detail="Business name not found")

    business.city = data.city
    await business.save()
    return {"message": f"City has been changed to {business.city}"}


@router.delete("/")
async def delete_business(b_name: str):
    try:
        name = await Bussiness.get_or_none(b_name=b_name)
        if not name:
            raise HTTPException(status_code=404, detail="Invalid bussiness name")
        await name.delete()
        return {"message": f"Business name has been deleted {b_name}"}
    except HTTPException as e:
        raise HTTPException(status_code=404, detail="Business name ot found")
