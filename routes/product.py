from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from models import (
    User,
    Product,
    Product_Pydantic,
    ProductIn_Pydantic,
    Bussiness,
    Update_Product,
)
from authentication import get_user
from util import des
from datetime import date
from util import prod_des


router = APIRouter()


@router.post("/create")
async def create_product(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    discount: int = Form(...),
    offer_expiration_date: date = Form(...),
    image: UploadFile = File(...),
    # bussiness: str = Form(...),
    user: User = Depends(get_user),
):
    try:
        business = await Bussiness.filter(owner=user).first()

        # business = await Bussiness.get_or_none(owner=user)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User has no business"
            )
        # upload image
        file_path = prod_des / f"{name}_{image.filename}"
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)

        product = {
            "name": name,
            "category": category,
            "price": price,
            "discount": discount,
            " offer_expiration_date": offer_expiration_date,
            "image": file_path,
            "bussiness": business,
        }
        new_product = await Product.create(**product)
        product_data = await Product_Pydantic.from_tortoise_orm(new_product)

        return {
            "message": f"Product is created with Category {new_product.id}",
            "product": product_data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create product: {str(e)}",
        )


@router.get("/orders")
async def get_orders(user: User = Depends(get_user)):
    return {"user": user}


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    print(file.filename)
    fn = des / file.filename
    print(file.content_type)
    content = await file.read()
    with open(fn, "wb") as f:
        f.write(content)
    return fn


@router.get("/get_file")
async def get_file():
    filename = "a.txt"
    url = f"http://127.0.0.1:8000/files/profile/h.py"
    return url


@router.get("/All_Products")
async def get_all_products():
    product = await Product.all()
    return product


@router.get("/Get_product_by_id ")
async def get_product(product_id: int):
    try:
        product = await Product.get(id=product_id)
        return await Product_Pydantic.from_tortoise_orm(product)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Id not found {e}"
        )


@router.put("/update_product")
async def update_product_by_id(data: Update_Product):
    product = await Product.get_or_none(id=data.id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prodcut not found"
        )

    product.price = data.price
    product.discount = data.discount
    await product.save()
    return {
        "message": f"Product has been changed {product.price} and {product.discount}"
    }


@router.delete("/Delete")
async def delete_product(id: int):
    print(id)
    product = await Product.get_or_none(id=id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prodcut not found"
        )
    await product.delete()
    return {"message": f"Product has been deleted {product}"}


# TODO
# get  products by category
# update product by taking some optional
# delete product by id
@router.get("/category")
async def get_category(category: str):
    try:
        product = await Product.get_or_none(category=category)
        return product
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found {e}"
        )
