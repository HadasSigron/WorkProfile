# Use the official Python base image
FROM python:3.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY static ./static
COPY templates ./templates
COPY app.py dbcontext.py person.py ./

# Expose the port
EXPOSE 5000

# Set the entry point
ENTRYPOINT ["python3", "app.py"]
