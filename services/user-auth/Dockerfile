# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that FastAPI will run on
EXPOSE 10000

# Set environment variables
ENV PYTHONPATH=/app
ENV PGSSLMODE=require
ENV HOST=0.0.0.0
ENV PORT=10000

# Run the application
CMD ["sh", "-c", "echo 'Variables de entorno:' && env && echo 'DB_USER: $DB_USER' && echo 'DB_PASSWORD: $DB_PASSWORD' && echo 'DB_HOST: $DB_HOST' && echo 'DB_PORT: $DB_PORT' && echo 'DB_NAME: $DB_NAME' && uvicorn app.main:app --host $HOST --port $PORT"]