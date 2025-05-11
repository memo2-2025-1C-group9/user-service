# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that FastAPI will run on
EXPOSE $PORT

# Command to run the FastAPI app with Uvicorn
# CMD ["sh", "-c", "uvicorn app.main:app --host $HOST --port $PORT"]

# Establecer la variable de entorno PYTHONPATH para que pytest encuentre el módulo app
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8080

# Ejecutar el script de entrada cuando el contenedor se inicie
ENTRYPOINT ["/app/entrypoint.sh", "app"]