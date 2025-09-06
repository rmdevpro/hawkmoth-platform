# Test small file
from fastapi import FastAPI

app = FastAPI(title="ACNE Test")

@app.get("/")
def read_root():
    return {"message": "ACNE is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
