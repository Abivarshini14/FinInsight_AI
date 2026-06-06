import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

os.environ["OPENAI_API_KEY"] = "your_api_key_here"

loader = TextLoader("data.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(docs, embeddings)

retriever = db.as_retriever()

llm = OpenAI(temperature=0)

qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

print("💰 FinInsight AI (type 'exit' to quit)\n")

while True:
    query = input("You: ")

    if query.lower() == "exit":
        break

    result = qa.run(query)
    print("AI:", result)