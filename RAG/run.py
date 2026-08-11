import json
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma

# Global variable to hold the vector store instance
VECTOR_STORE = None
load_dotenv()

@tool
def load_vector_db() -> str:
    """
    Tool to load the vector database.
    You must ALWAYS call this tool FIRST before using the search_embeddings tool.
        
    Returns:
        str: Success message indicating the database was loaded.
    """
    global VECTOR_STORE
    print("loading embedding model...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")

    print("loading vector db")
    VECTOR_STORE = Chroma(
        persist_directory=r"D:\projects\AgenticAI_Practice\RAG\chroma_db",
        embedding_function=embeddings
    )
    return "Vector database loaded successfully. You can now use the search_embeddings tool."

@tool
def search_embeddings(query: str, top_k: int = 2) -> str:
    """
    Search for similar content in the loaded vector database based on a query.
    Make sure load_vector_db was called successfully before using this tool.
    
    Args:
        query (str): Natural language search query.
        top_k (int): top most results found. Default is 2.
        
    Returns:
        str: A JSON string containing the structured search results.
    """
    global VECTOR_STORE
    if VECTOR_STORE is None:
        return "Error: Vector database is not loaded. Please call load_vector_db first."
        
    print(f"searching for '{query}'...")
    # Retrieve top_k documents using similarity search
    docs = VECTOR_STORE.similarity_search(query, k=top_k)
    
    # Create a clean structured data format
    structured_results = []
    for index, doc in enumerate(docs, start=1):
        structured_results.append({
            "rank": index,
            "content": doc.page_content,
            "metadata": doc.metadata
        })
            
    return json.dumps(structured_results, indent=4, ensure_ascii=False)


from langchain.agents import create_agent

def run_agent(query: str):
    """
    Initializes the LLM and the Agent, then runs the query.
    """
    # 1. Initialize LLM
    print("initializing LLM...")
    llm = init_chat_model(
        model="gemini-3.5-flash-lite",
        model_provider="google-genai"
    )
    
    # 2. Define tools
    tools = [load_vector_db, search_embeddings]
    
    # 3. Create the System Prompt
    system_prompt = (
        "You are an intelligent assistant specifically for question-answering tasks.\n"
        "To answer the user's question, you must follow these steps in order:\n"
        "1. FIRST, use the `load_vector_db` tool to load the database.\n"
        "2. THEN, use the `search_embeddings` tool to retrieve the context related to the user's question.\n"
        "3. FINALLY, use the retrieved context to formulate a concise answer.\n"
        "If the answer is not included in the given information, inform the user you don't know the answer in a respectful and polite way.\n"
        "Always provide and verify the answer from the retrieved context only."
    )
    
    # 4. Create Agent
    agent = create_agent(
        model=llm, 
        tools=tools, 
        system_prompt=system_prompt
    )
    
    # 5. Invoke the Agent
    print(f"\n--- Running Agent for Query ---\n")
    # create_agent returns a LangGraph compiled graph which takes "messages" as input
    response = agent.invoke({
        "messages": [("user", query)]
    })
    
    print("\n================ FINAL RESPONSE ================\n")
    # The last message in the response is the agent's final answer
    final_message = response["messages"][-1]
    print(final_message.content)
    print("\n================================================\n")

if __name__ == "__main__":

    user_query = "what are types of AI agents?"
    run_agent(query=user_query)