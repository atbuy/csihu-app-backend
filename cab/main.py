from fastapi import FastAPI

app = FastAPI()


@app.get("/notifications")
async def notifications():
    return {"message": "Hello, World"}
