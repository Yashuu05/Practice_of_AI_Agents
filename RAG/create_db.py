from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from pathlib import Path

class CreateEmbeddings:

    def __init__(self):
        pass 

    def create_embeddings(self, corpus_path: Path | str) -> None:
        """
        - *purpose*: converts raw corpus into vectors and stored into vector database
        - *input*: corpus_path (path of document)
        """

        # load doc
        try: 
            loader = TextLoader(corpus_path)
            documents = loader.load()

            # split text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100
            )
            docs = text_splitter.split_documents(documents)
            print(f"split into {len(docs)} chunks")

            # define embedding model
            embeddings = OllamaEmbeddings(
                model="nomic-embed-text:v1.5"
            )
            print("emeddings model ready")

            # store into chromadb
            vector_store = Chroma.from_documents(
                docs,
                embedding=embeddings,
                persist_directory="./chroma_db"
            )
        
            vector_store.persist()
            print("vector database created and saved.")

        except Exception as e:
             print(f"error: {e}")


if __name__ == "__main__":
    print("==== PORGRAM INITIATED =====")

    emd = CreateEmbeddings()
    emd.create_embeddings(corpus_path=r"D:\projects\AgenticAI_Practice\RAG\corpus.txt")

    print("==== PROGRAM TERMINATED =====")