# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

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
CMD ["/app/entrypoint.sh", "app"]