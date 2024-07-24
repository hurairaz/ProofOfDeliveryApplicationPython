from fastapi import FastAPI
from database import engine
import models
from routers import auth
from routers import dispatches

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(dispatches.router, prefix="/api")
