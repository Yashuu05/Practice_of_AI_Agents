from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

print("loading embedding model...")
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5"
)
print("Embeddings loaded")

print("loading vector db")
vectorstore = Chroma(
    persist_directory="D:\projects\AgenticAI_Practice\RAG\chroma_db",
    embedding_function=embeddings
)

# Configure retriever to fetch the top 5 closest matching chunks
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})


# 1. System prompt defining AI boundaries and injecting context
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, say that you don't know.\n\n"
    "Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}"),
])

# 2. Initialize the LLM
print("initalizing LLM...")
llm = OllamaLLM(model="gemma3:1b", temperature=0.5)

# 3. Helper to merge retrieved document contents into a single text block
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 4. Construct the complete execution pipeline (LCEL)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print("reponse=\n")
response = rag_chain.invoke("What is AI Agent?")
print(response)
