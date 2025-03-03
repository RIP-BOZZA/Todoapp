from fastapi import APIRouter ,Depends ,HTTPException ,Path
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel ,Field
from models import Todos


router=APIRouter()




# create a db session for using in all apis
"""
what is doing ,since we use yield db ,it will only execute the code before the yield ,
finally only execute wehn the response is returned ,this can make our fastapi faster ,safe,all sessions closed after use
"""
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally :
        db.close()


"""
depends - dependancy injection -- means run something before execution of api .this will allow some to run in behind the scnes
Annotated[Session,Depends(get_db)] -- this code used to add additonal metadata with the dependancy injection

"""
db_dependancy =Annotated[Session,Depends(get_db)] # dependancy injection


class TodoRequest(BaseModel):
    title :str = Field(min_length=3)
    description:str =Field(min_length=3,max_length=100)
    priority :int =Field(gt=0)
    complete:bool


@router.get("/")
async def read_all(db:db_dependancy):
    return db.query(Todos).all()


@router.get("/todo/{todo_id}" ,status_code=status.HTTP_200_OK)
async def read_todo(db:db_dependancy,todo_id:int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404 ,detail="id not found")


@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(db:db_dependancy ,todo_request:TodoRequest):
    todo_model =Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependancy,todo_request:TodoRequest 
                      ,todo_id:int=Path(gt=0)):
    todo_model =db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description=todo_request.description
        todo_model.priority=todo_request.priority
        todo_model.complete =todo_request.complete
        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404 ,detail="id related obj not found")


@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependancy ,todo_id:int =Path(gt =0)):
    todo_model =db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="todo model not found")

    todo_model =db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()
