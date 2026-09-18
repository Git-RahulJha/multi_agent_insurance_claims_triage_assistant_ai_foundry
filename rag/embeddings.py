import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")


client = OpenAI(
    api_key=api_key,
    base_url=endpoint,
)

# it will generate an embedding vector for the given text using the specified deployment in Azure OpenAI Service
def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=deployment,
        input=text,
    )

    return response.data[0].embedding

if __name__ == "__main__":
    vector = generate_embedding(
        "Claims filed shortly after policy inception "
        "should be flagged for review."
    )

    print(f"Embedding dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")