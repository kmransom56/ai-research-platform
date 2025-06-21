FROM python:3.12-slim

WORKDIR /app

COPY magentic_one_server.py magentic_one_server.py
COPY magentic_one_implementation.py magentic_one_implementation.py

# Install FastAPI and Uvicorn
RUN pip install uv
RUN uv pip install --system fastapi uvicorn autogen-agentchat "autogen-ext[magentic-one,openai]" openai tiktoken playwright
RUN playwright install --with-deps chromium

EXPOSE 11003

CMD ["uvicorn", "magentic_one_server:app", "--host", "0.0.0.0", "--port", "11003"]
