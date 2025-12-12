from fastapi import FastAPI

app = FastAPI()


@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.post("/api/upload")
async def uploadFile():


    pass