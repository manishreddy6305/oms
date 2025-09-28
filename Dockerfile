# Use official Python base image
FROM python:3.11-slim


RUN pip install python-dotenv
RUN pip install boto3
RUN apt-get update && apt-get install -y docker.io
RUN pip install --no-cache-dir pymongo
RUN pip install --no-cache-dir fastapi uvicorn[standard]


# Set working directory inside container
WORKDIR /app

# Copy your Python code into the container
COPY . .

EXPOSE 8000


# Set environment variables (optional default values, can override at runtime)

# Command to run your Python app
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
