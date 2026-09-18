import json
from google import genai
from google.genai import errors as genai_errors
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import GEMINI_API_KEY, GENERATION_MODEL, EMBEDDING_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

_retry_on_server_error = retry(
    retry=retry_if_exception_type(genai_errors.ServerError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    reraise=True,
)

@_retry_on_server_error
def generate(prompt: str) -> str:
    response = client.models.generate_content(model=GENERATION_MODEL, contents=prompt)
    return response.text or ""

@_retry_on_server_error
def embed(text: str) -> list[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={"output_dimensionality": 768},
    )
    return list(result.embeddings[0].values)

def extract_json(prompt: str) -> dict:
    raw = generate(prompt)
    raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(raw)