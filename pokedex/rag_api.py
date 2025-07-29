from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from operator import itemgetter
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv(override=True)

# CONFIG
db_dir = os.getenv('DB_DIRECTORY')
collection = os.getenv('COLLECTION_NAME')
llm_model = os.getenv('LLM_MODEL_NAME')
model_name = os.getenv('EMBEDDING_MODEL_NAME')

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],  # or ["*"] for local testing only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory history store (you can improve this later with session support)
history = []

# Embedding and retrieval
embedding_model = OllamaEmbeddings(model=model_name)
vector_store = Chroma(
    collection_name=collection,
    persist_directory=db_dir,
    embedding_function=embedding_model
)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Prompt
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

llm = OllamaLLM(model=llm_model, temperature=0.0, streaming=True)

# Chain
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

# Request schema
class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_pokedex(req: AskRequest):
    global history
    if len(history) > 10:
        history = history[-10:]

    def stream_response():
        full_response = ""
        for chunk in chain.stream({
            "question": req.question,
            "history": history
        }):
            full_response += chunk
            yield chunk
        history.append(HumanMessage(content=req.question))
        history.append(AIMessage(content=full_response))

    return StreamingResponse(stream_response(), media_type="text/plain")
