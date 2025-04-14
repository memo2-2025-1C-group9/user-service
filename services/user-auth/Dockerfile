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

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port 10000