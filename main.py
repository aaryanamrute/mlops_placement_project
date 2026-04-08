from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import logging
from fastapi import Request
from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.security import APIKeyHeader

logging.basicConfig(level=logging.INFO)


app = FastAPI()

# Load model (VERY IMPORTANT: keep at top)
model = pickle.load(open("model.pkl", "rb"))

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.url}")
    response = await call_next(request)
    logging.info(f"Status: {response.status_code}")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Error: {str(exc)}")
    return {"error": "Something went wrong"}

api_key_header = APIKeyHeader(name="x-api-key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != "12345":
        raise HTTPException(status_code=401, detail="Unauthorized")


# Input schema
class Student(BaseModel):
    cgpa: float
    iq: int
    projects: int
    internships: int
    communication: int

# Prediction API
@app.post("/predict")
def predict(data: Student, key: str = Depends(verify_api_key)):
    features = [[
        data.cgpa,
        data.iq,
        data.projects,
        data.internships,
        data.communication
    ]]

    result = model.predict(features)

    return {"placement": int(result[0])}