# Use a lightweight Python 3.11 base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and force stdout logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# Create the standard data and configuration directories
RUN mkdir -p data/in_dat data/out_dat topology/sources topology/sinks/business.d

# By default, run the daemon when the container starts
CMD ["wparse", "daemon"]