from azure.identity import DefaultAzureCredential

#from rag.ingestion import ingest
from rag.retriever import retrieve


def authenticate():
    credential = DefaultAzureCredential()

    token = credential.get_token(
        "https://management.azure.com/.default"
    )

    print("Azure authentication successful")
    print(f"Token acquired: {token.token[:20]}...")

def main():
    #retrieve("A claim was filed shortly after the policy started. Should it be reviewed?")
    retrieve("Claims reported more than 7 days")

if __name__ == "__main__":
    main()