# from fastapi import File, UploadFile
from pathlib import Path

UPLOAD_DIR = Path("upload")
des = UPLOAD_DIR / "profile"
des.mkdir(parents=True, exist_ok=True)

# Product destination for image
prod_des = UPLOAD_DIR / "product"
prod_des.mkdir(parents=True, exist_ok=True)
