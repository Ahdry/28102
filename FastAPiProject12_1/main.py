from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time

DATABASE_URL = "postgresql://username:password@localhost/dbname"  # Укажите свои данные

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    created_at = Column(TIMESTAMP)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: constr(min_length=1, max_length=255)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    start_time = time.time()
    db: Session = SessionLocal()
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    elapsed_time = time.time() - start_time
    print(f"Время затраченное на регистрацию: {elapsed_time:.4f} секунд")
    return db_user

@app.get("/users/", response_model=list[UserResponse])
def get_users():
    db: Session = SessionLocal()
    users = db.query(User).all()
    return users

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    return {"detail": "Пользователь успешно удален"}

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)