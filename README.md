
## Setup & Run

1. **Clone the repo:**

```bash
git clone https://github.com/alokrajmindfire/chat-bot
cd chat-bot
```

2. **Install dependencies with Poetry:**

```bash
poetry install
```

3. **Activate virtual environment:**

```bash
poetry env activate

**For windows**
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate.ps1
```

4. **Add api key:**

```bash
 $env:LLM_API_KEY="******" 
```

5. **Run the app:**

```bash
poetry run poe dev
```

6. **Open in browser:**
   [http://127.0.0.1:8000](http://127.0.0.1:8000)

---




<!-- Logging -->