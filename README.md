# ☁️ CloudWalk Chatbot

This project implements a Retrieval-Augmented Generation (RAG) chatbot using the FastAPI framework. 
The chatbot is designed to provide information about CloudWalk, its products (like InfinitePay), mission, and brand values by leveraging external data sources.

## Prerequisites

Ensure you have the following installed on your system:

* **Python** (3.8+)
* **Git**
* **uv** (The extremely fast Python package manager)

## 1. Setup and Installation

Follow these steps to get your local environment running using `uv`:

### 1.1 Clone the Repository

Clone the project repository to your local machine:

```bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name
````

### 1.2 Create Virtual Environment and Install Dependencies (using uv)

`uv` simplifies the process by creating the virtual environment and installing dependencies in one go. The environment will be created in a default `.venv` directory.

```bash
# Initialize uv 
uv sync
```

## 2\. Configuration

This application requires an OpenAI API key for the core LLM functionality.

### 2.1 Set Environment Variables

Create a file named **`.env`** in the root directory of the project and add your API key:

```.env
OPENAI_API_KEY="sk-your-openai-api-key-here"
# Optional: Specify the model (default is gpt-4o-mini)
OPENAI_MODEL="gpt-4o"
```

The application uses the `python-dotenv` package to load these variables automatically at startup.

## 3\. Running the Application

The chatbot is served using FastAPI, which is run via `uvicorn`.

### Run Command

Execute the following command from the project root directory (`your-repo-name`). The use of `uv run` ensures the script is executed within the project's virtual environment (`.venv`) whether it's explicitly activated or not:

```bash
uv run uvicorn app:app --reload
```

  * `app:app` refers to the FastAPI application instance named `app` inside the **`app.py`** file.
  * `--reload` enables hot-reloading for development.

### Accessing the API

Once running, the application will be accessible at:

  * **API Endpoint:** `http://127.0.0.1:8000/`
  * **Interactive Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`
  * **Redoc Documentation:** `http://127.0.0.1:8000/redoc`

Use the `/docs` page to interact with the chat endpoint (e.g., `/chat`) to test the RAG functionality.

```
```