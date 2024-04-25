import uvicorn
from fastapi import FastAPI

from .routers.api_contoller import router as api_controller_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(api_controller_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
