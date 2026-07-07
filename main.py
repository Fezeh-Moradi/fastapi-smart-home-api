from fastapi import FastAPI

from routers import auth, users, devices

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(devices.router)


@app.get("/")
def root():
    return {
        "message": "Smart Home API is running"
    }


