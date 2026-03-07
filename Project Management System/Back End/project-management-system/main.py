from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, project, task, signup, login
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# origins = [
#     "http://127.0.0.1:5500",
#     "http://localhost:5500",
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(signup.router)
app.include_router(login.router)