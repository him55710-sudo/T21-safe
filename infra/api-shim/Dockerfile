FROM python:3.12-slim
WORKDIR /app
RUN groupadd --system api && useradd --system --gid api api
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
USER api
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
