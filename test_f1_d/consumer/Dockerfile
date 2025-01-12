FROM python:3.10-slim

# Install nc (netcat) tool
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Install any additional dependencies for your application
WORKDIR /app
COPY . /app

# Install your Python dependencies
RUN pip install -r requirements.txt

# Start the application
CMD ["python", "consumer.py"]
