import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from rag.models import RetrievedChunk
from rag.embeddings import generate_embedding

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_AI_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX")


search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY),
)

# this function performs a vector search or hybrid keyword + vector search on the Azure AI Search index
def search_knowledge(query: str, top_k: int = 3, hybrid: bool = True) -> list[RetrievedChunk]:
    """
    Search insurance knowledge using vector search
    or hybrid keyword + vector search.
    """
    query_vector = generate_embedding(query)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="content_vector",
    )

    results = search_client.search(
        search_text=query if hybrid else None,
        vector_queries=[vector_query],
        select=["id", "title", "content", "category", "source", "chunk_id"],
        top=top_k
    )

    #return list(results)
    return [
        RetrievedChunk(
            id=result["id"],
            title=result["title"],
            content=result["content"],
            category=result["category"],
            source=result["source"],
            chunk_id=result["chunk_id"],
            score=result.get("@search.score", 0.0),
        )
        for result in results
    ]

# this function retrieves relevant knowledge chunks based on the query and prints the results
def retrieve(query: str):
    results = search_knowledge(query, top_k=3, hybrid=True)

    if not results:
        print("No relevant information found.")
        return

    print(f"\nQuery: {query}\n")

    for index, result in enumerate(results, start=1):
        print("=" * 70)
        print(f"Result #{index}")
        print(f"Score: {result.score}")
        print(f"Source: {result.source}")
        print(f"Chunk: {result.chunk_id}")
        
        print(f"Category : {result.category}")
        print("\nContent:")
        print(result.content)


#if __name__ == "__main__":
#    retrieve("A claim was filed shortly after the policy started. Should it be reviewed?")
