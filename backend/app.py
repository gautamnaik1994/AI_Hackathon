from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.llm import LLM_Api
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
import time

load_dotenv()

app = FastAPI()
origins = [
    "http://localhost:3000",  # React app running on localhost:3000
    "http://localhost:8000",  # FastAPI server running on localhost:8000
    "http://localhost:5173",  # Streamlit app running on localhost:8501
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api = LLM_Api(model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", temperature=0.0,
              api_key=os.environ["TOGETHER_AI_API_KEY"], chatbot_type="qa")


class QABody(BaseModel):
    question: str = Field(default="What is React?")
    answer: str = Field(
        default="React is a JavaScript library used for building user interfaces.")
    subject: str = Field(default="ReactJS")


class ResponseBody(BaseModel):
    rating: float
    reason: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/rate_qa", response_model=ResponseBody)
def rate_qa(qa_body: QABody):
    question = qa_body.question
    answer = qa_body.answer
    subject = qa_body.subject
    print(question, answer, subject)
    # time.sleep(1)
    try:
        res = api.rate_answer(question, answer, subject)
        return JSONResponse(status_code=200, content={**res})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred")