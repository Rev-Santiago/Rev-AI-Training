# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements first (to leverage Docker caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Expose the port FastAPI runs on
EXPOSE 8000

# 7. Command to run the app
# We use 0.0.0.0 so it can be accessed from outside the container (like by the TV)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]