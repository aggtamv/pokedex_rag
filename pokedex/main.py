import sys
import pyfiglet

# for db
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# for io
import mysql.connector
import json
from operator import itemgetter
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv(override=True)  # Load environment variables from .env file
# Connection to MySQL DB
conn = mysql.connector.connect(
    host= os.getenv('DB_HOST'     , None),
    user= os.getenv('DB_NAME', None),
    password= quote_plus(os.getenv('DB_PASSWORD'     , None)),
    database= os.getenv('DB_NAME'     , None)
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM Pokemon")
rows = cursor.fetchall()
cursor.close()
conn.close()

# global for easy changes
db_dir = os.getenv('DB_DIRECTORY'     , None)
collection = os.getenv('COLLECTION_NAME'     , None)
llm_model = os.getenv('LLM_MODEL_NAME'     , None)
model_name = os.getenv('EMBEDDING_MODEL_NAME'     , None)

# load data to db (to rerun please remove DB_DIRECTORY)
def db():
    embedding_model = OllamaEmbeddings(model=model_name)
    vector_store = Chroma(
        collection_name=collection,
        persist_directory=db_dir,
        embedding_function=embedding_model
    )

    # Converting rows into LangChain Documents
    docs = []
    for row in rows:
        content = f"""
        Name: {row['name']}
        Dex ID: {row['id']}
        Types: {json.loads(row['types'])}
        Abilities: {json.loads(row['abilities'])}
        Height: {row['height']} m
        Weight: {row['weight']} kg
        Base Stats: {json.loads(row['base_stats'])}
        Moves: {json.loads(row['moves'])}
        Cry URL: {row['cry_url']}
        """
        doc = Document(page_content=content, metadata={"source": f"pokemon:{row['id']}"})
        docs.append(doc)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Split into chunks
    chunks = splitter.split_documents(docs)
    print("db: Data cleaned and splitted into consistent chunks.")

    vector_store.add_documents(chunks)
    print(f"db: {len(chunks)} chunks added in vector store.")

# make questions to ai actuall rag
def io():
    embedding_model = OllamaEmbeddings(model=model_name)
    vector_store = Chroma(
        collection_name=collection,
        persist_directory=db_dir,
        embedding_function=embedding_model
    )
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    prompt = """
    You are a Pokédex — a highly intelligent, encyclopedic database of all known Pokémon from the Pokémon universe. Your role is to provide comprehensive, clear, and accurate information about any Pokémon when asked.

    When a Pokémon name is provided, respond with the following structured format:

    Name:
    National Dex Number:
    Type(s):
    Species:
    Height:
    Weight:
    Abilities:
    Base Stats (HP / Atk / Def / Sp. Atk / Sp. Def / Speed):
    Evolutions:
    Habitat/Location:
    Notable Moves (Level-Up, TM/TR, Egg, Tutor):
    Pokédex Entry (Flavored Description):
    Fun Fact / Trivia:

    Additional Guidelines:
    - Keep entries concise yet rich in detail.
    - Use accurate Pokémon data up to Generation IX (Scarlet & Violet), unless instructed otherwise.
    - If a Pokémon has regional forms (e.g., Alolan, Galarian), list them too.
    - Avoid speculation — stick to canonical information.
    - Format the information clearly using headings and bullet points when helpful.
    - If the input is vague (e.g., "fire starters"), ask clarifying questions or list matching Pokémon.
    - Your tone should be informative and friendly, much like a real Pokédex would sound in the games or anime.

    Context:
    {context}

    History:
    {history}

    Question:
    {question}
    """

    prompt_template = PromptTemplate(
        input_variables=["context", "question", "history"],
        template=prompt
    )

    llm = OllamaLLM(
        model=llm_model,
        temperature=0.0,
        streaming=True
    )

    chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question"),
            "history": itemgetter("history")
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    history = []
    while True:
        q = input("ask > ")
        if q.strip().lower() == 'q':
            print("\nBye")
            break

        output = ""

        # avoid errors for the prompt size of llm
        if len(history) > 10:
            history = history[-10:]

        for token in chain.stream({"question": q, "history": history}):
            print(token, end="", flush=True)
            output += token
        print("\n")

        history.append(HumanMessage(content=q))
        history.append(AIMessage(content=output))

def main():
    try:
        run = sys.argv[1]
        if run.strip().lower() == 'io':
            ascii_banner = pyfiglet.figlet_format("rag v1 - io")
            print(ascii_banner)

            io()
        else:
            ascii_banner = pyfiglet.figlet_format("rag v1 - db")
            print(ascii_banner)

            db()
    except IndexError as e:
        print("try: python main.py [db|io]")

if __name__ == "__main__":
    main()