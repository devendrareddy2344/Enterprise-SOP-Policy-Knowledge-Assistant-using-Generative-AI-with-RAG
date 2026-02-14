FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory into the container
COPY app /app/app
# Copy the .env file (for local dev instructions, usually omitted in prod/git handling)
COPY .env .

EXPOSE 8000

# Updated CMD to point to app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
