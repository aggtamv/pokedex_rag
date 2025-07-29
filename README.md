# 🧠 Pokédex RAG App

A full-stack Pokémon Pokédex app built with **Flask** and enhanced with a **Retrieval-Augmented Generation (RAG) Agent** powered by an **LLM**. This project combines a classic web interface with cutting-edge AI to provide deep, structured insights into any Pokémon.

---

## 📖 Project Description

This application features:

- 🎨 A **Flask**-based frontend for browsing, filtering, and viewing Pokémon
- 🔍 An integrated **RAG agent** exposed via **FastAPI**, capable of answering Pokémon-related questions using LLM-powered responses
- 🧠 Uses **ChromaDB** as a vector store to retrieve relevant context
- 🤖 Powered by the **Mistral** LLM (via [Ollama](https://ollama.com))
- 🧬 Embeddings generated using `jeffh/intfloat-multilingual-e5-large:f32`
- 🗄️ The RAG data (Pokémon context) is loaded from a **MySQL** database created with **MySQL Workbench**

The FastAPI backend handles RAG logic, while Flask fetches and displays the rich data in a user-friendly interface.

---

## 🚀 Local Setup (Without Docker)

> 🐍 Requirements:
> - Python 3.13
> - [Ollama](https://ollama.com/) installed and running
> - MySQL Server and MySQL Workbench installed (to set up your database)

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pokedex-rag.git
cd pokedex-rag
```

---

### 2. Set Up a Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate 

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Up the Environment Variables

Create a `.env` file in the project root:

```env
# .env
DB_DIRECTORY=chromadb
COLLECTION_NAME=pokedex
LLM_MODEL_NAME=mistral:latest
EMBEDDING_MODEL_NAME=jeffh/intfloat-multilingual-e5-large:f32
```

---

### 5. Prepare the MySQL Database

Use **MySQL Workbench** to create a database (e.g., `pokedex`) and import or insert Pokémon data that will serve as the RAG context.

Make sure your data includes meaningful text fields per Pokémon (stats, moves, lore, etc.).

---

### 6. Start Ollama

Make sure [Ollama](https://ollama.com) is installed and running.

Then pull required models:

```bash
ollama pull mistral
ollama pull jeffh/intfloat-multilingual-e5-large:f32
```

---

### 7. Run the FastAPI RAG Agent

```bash
uvicorn app.rag_api:app --host 0.0.0.0 --port 8000
```

---

### 8. Run the Flask App

In a separate terminal:

```bash
export FLASK_APP=app.main   # or set FLASK_APP=app.main.py on Windows
flask run --port 5000
```

---

### ✅ You’re all set!

- Visit the frontend: [http://localhost:5000](http://localhost:5000)
- Test the RAG API: [http://localhost:8000/ask](http://localhost:8000/ask)

---

## 🧠 Credits

- [PokéAPI](https://pokeapi.co/)
- [LangChain](https://www.langchain.com/)
- [Ollama](https://ollama.com/)
- [ChromaDB](https://www.trychroma.com/)
- [MySQL](https://www.mysql.com/)

---

