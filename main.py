from fastapi import FastAPI

app = FastAPI(title="AnimePass")

@app.get("/")
def home():
    return {"message": "AnimePass запускается!"}
