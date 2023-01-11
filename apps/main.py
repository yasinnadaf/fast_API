from typing import Optional

from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    rating: Optional[int] = None


# @app.get("/")
# def root():
#     return {"message": "Hello World !!"}
#
#
# @app.get("/post")
# def root():
#     return {"message": "second method"}
#
#
# @app.post("/creating_post")
# def create():
#     return {"msg": "post created successfully"}


# @app.post("/creating_posts")
# def create(payload: dict = Body(...)):  # extracting data from body postmen
#     print(payload)
#     return {"msg": "post created successfully"}


@app.post("/creating_postss")
def create(new_post: Post):  # sending back to api server
    # print(new_post.rating)
    print(new_post.dict)
    return {"data": new_post}  # sending back to api server
