from fastapi import FastAPI
import logging
import uuid
import json
import requests
from pydantic_models import QueryInput, QueryResponse

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

app = FastAPI()


def get_llm():
    from openai import OpenAI

    llm_client = OpenAI(
        base_url="http://localhost:8001/v1",
        api_key="dummy",
    )
    return llm_client


llm = get_llm()


@app.get("/")
def read_root():
    logger.info("This is an info message from FastAPI")
    return {"message": "Check your logs!"}


@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id
    logging.info(
        f"Session ID: {session_id}, User Query: {query_input.query}, Model: {query_input.model}"
    )
    if not session_id:
        session_id = str(uuid.uuid4())

    # answer = "hao ai hao ai ni"
    resp = llm.chat.completions.create(
        # model="Llama-3.1-8B-Instruct",
        model="/home/yhj2263/llama/models/Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": query_input.query}],
    )
    logger.info(f"{resp=}")
    # resp_json = json.loads(resp)
    answer = resp.choices[0].message.content
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)
