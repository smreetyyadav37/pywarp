# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies (added setuptools to fix the pyproject.toml bug)
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN pip install -r requirements.txt
RUN pip install -e .

# Expose Streamlit's default port
EXPOSE 10000

# Command to run the dashboard
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]