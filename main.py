from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import ssl

app = FastAPI()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('./certificate/certificate.pem', keyfile='./certificate/key.pem')

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=3000, ssl=ssl_context, reload=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}