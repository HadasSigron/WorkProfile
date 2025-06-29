# First stage: Builder
# We use the same base image as your original Dockerfile for consistency
FROM python:3.9-bullseye AS builder

# Set up the working directory for our build stage
WORKDIR /app

# Copy and install dependencies in the builder stage
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: Production
# We use Alpine to create a much smaller final image
FROM python:3.9-alpine

# Set up the working directory in our production image
WORKDIR /app

# Copy Python packages from the builder stage
# Note how we copy from the specific Python version directory
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy application files
# We copy these directly from our host, not the builder stage
COPY static ./static
COPY templates ./templates
COPY app.py dbcontext.py person.py ./

# Expose the port - keeping your original port configuration
EXPOSE 5000

# Set the entry point - same as your original
ENTRYPOINT ["python3", "app.py"]
