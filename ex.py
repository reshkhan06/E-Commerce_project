from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

KEYS = os.getenv("SECRET")
data = {"userid": "user123", "name": "resham"}
token = jwt.encode(data, key=KEYS, algorithm="HS256")

print(token)
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiJ1c2VyMTIzIiwibmFtZSI6InJlc2hhbSJ9.f-kOXv2uu1GH6uDb9eD4KixCRNfJJRxQUm_h8ms"
decoded = jwt.decode(token=token, key=KEYS, algorithms=["HS256"])
print(decoded)
