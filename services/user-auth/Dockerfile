# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for SSL certificates
RUN mkdir -p /etc/ssl/certs

# Copy script entrypoint into the container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port that FastAPI will run on
EXPOSE $PORT

# Establecer la variable de entorno PYTHONPATH para que pytest encuentre el módulo app
ENV PYTHONPATH=/app
ENV PGSSLMODE=require

# Ejecutar el script de entrada cuando el contenedor se inicie
ENTRYPOINT ["/entrypoint.sh"]