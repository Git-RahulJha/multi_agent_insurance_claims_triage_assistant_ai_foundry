import os

from pathlib import Path
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

from rag.embeddings import generate_embedding

load_dotenv()


SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_AI_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX")
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

credential = AzureKeyCredential(SEARCH_KEY)

index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=credential,
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY),
)


# this function creates an index in Azure AI Search if it doesn't exist, otherwise it updates the existing index
def create_index():

    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
        ),

        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
        ),

        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),

        SearchableField(
            name="category",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SearchableField(
            name="source",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="insurance-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="insurance-hnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="insurance-vector-profile",
                algorithm_configuration_name="insurance-hnsw",
            )
        ],
    )

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
    )

    result = index_client.create_or_update_index(index)

    print(f"Index created successfully: {result.name}")

# we applied simple chunking logic to split the text into smaller chunks for embedding generation. You can adjust the chunk size and overlap as needed.
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == text_length:
            break

        start = end - overlap

    return chunks

# loads all markdown files from the knowledge directory and returns a list of documents with their metadata (source, title, content)
def load_documents():
    documents = []

    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        documents.append(
            {
                "source": path.name,
                "title": path.stem,
                "content": text,
            }
        )

    return documents

# chunks the content of each document and returns a list of chunked documents
def chunk_documents(documents=None):
    chunked_documents = []
    for document in documents:
        chunks = chunk_text(document["content"])

        print(f"{document['source']}: " 
              f"{len(chunks)} chunks")
        chunked_documents.append(chunks)

    return chunked_documents

# creates search documents by chunking the content of each document, 
# generating embeddings for each chunk, and preparing the data for ingestion into Azure AI Search index
def save_embedding(chunked_documents=None):
    search_documents = []
    for document in chunked_documents:
        chunks = chunk_text(document["content"])

        print(f"{document['source']}: " 
              f"{len(chunks)} chunks")
        chunked_documents.append(chunks)

        for index, chunk in enumerate(chunks):
            vector = generate_embedding(chunk)

            # it creates a search document with the chunked content, metadata, and embedding vector for ingestion into Azure AI Search index
            search_documents.append(
                {
                    "id": f"{document['title']}-{index}",
                    "title": document["title"],
                    "content": chunk,
                    "category": document["title"],
                    "source": document["source"],
                    "chunk_id": str(index),
                    "content_vector": vector,
                }
            )

    result = search_client.upload_documents(documents=search_documents)
    successful = sum(1 for item in result if item.succeeded)
    
    print(
        f"Uploaded {successful}/{len(search_documents)} "
        "documents successfully."
    )
    

def ingest():
    documents = load_documents()
    chunked_documents = chunk_documents(documents)
    save_embedding(chunked_documents)

if __name__ == "__main__":
    
    #create_index()
    ingest()