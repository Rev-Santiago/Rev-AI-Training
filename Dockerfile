FROM python:3.11-slim
WORKDIR /app

# Add this line to force a fresh build if you are still stuck
ARG CACHEBUST=1 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]