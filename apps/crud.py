from random import randrange
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.openapi.models import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from . import models, schemas, utils
from .database import engine, get_db
from .schemas import Post
from passlib.context import CryptContext

pwd_contex = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# class Post(BaseModel):
#     title: str
#     content: str
#     publish: bool = True
#     rating: Optional[int] = None


my_post = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
           {"title": "title of post 2", "content": "content of post 2", "id": 2}]


@app.get("/post")
def root():
    return {"data": my_post}


def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_post):
        if p['id'] == id:
            return i


@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):
    return {"status": "success"}


@app.post("/post")
def create(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 2000)
    my_post.append(post_dict)
    return {"data": post_dict}


@app.get("/post/{id}")
def get_post(id: int):
    post = find_post(id)
    print(post)
    return {"post": post}


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesnt exist")
    my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesnt exist")
    post_dict = post.dict()
    post_dict['id'] = id
    my_post[index] = post_dict
    return {"data": post_dict}


# ---------------------------------
# orm


@app.post("/create", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostBase, db: Session = Depends(get_db)):
    # new_post = models.Post(title=post.title, content=post.content, published=post.publish)
    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/get_post", response_model=List[schemas.Post])
def get_post(db: Session = Depends(get_db)):
    post = db.query(models.Post).all()

    return post


@app.get("/get_post/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesnt exist")
    return post


@app.put("/update_post/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    update_query = db.query(models.Post).filter(models.Post.id == id)
    post = update_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesnt exist")
    update_query.update(updated_post.dict())
    db.commit()
    return post


@app.delete("/delete_post/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} doesnt exist")
    post.delete()
    db.commit()
    return post


# -----------------------------------------
# user

@app.post("/user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pass = utils.hash(user.password)
    user.password = hashed_pass
    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#swagger new project chat registraion and login ...group text