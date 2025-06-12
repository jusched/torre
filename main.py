from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# App
app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
