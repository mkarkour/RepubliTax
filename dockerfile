# Étape de build
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /code

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .
COPY uv.lock .
COPY launcher.py .

# --- UV installation (optional) ---
# Uncomment the following section if you want to use UV instead of pip

# Install necessary system dependencies for UV
# RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Install UV (alternative to pip)
# ADD https://astral.sh/uv/install.sh /uv-installer.sh
# RUN sh /uv-installer.sh && rm /uv-installer.sh

# Set environment variable for UV installation
# ENV PATH="/root/.local/bin/:$PATH"

# --- Optional: Create a virtual environment with UV ---
# Uncomment the following lines if you want to use UV's virtual environment
# RUN uv venv .venv

# --- Install Python dependencies ---
# Choose one of the following methods to install dependencies:
#
# 1. Install dependencies using `pip` (default method)
RUN pip install -r requirements.txt
#
# 2. Install dependencies using `uv` (uncomment this line if you want to use UV)
# RUN uv pip install -r requirements.txt

# --- Copy the application source code ---
COPY app/ ./app/
COPY src/ ./src/
COPY test/ ./test/
COPY docs/ ./docs/

# Expose the port used by Streamlit
EXPOSE 8501

# Set the Python path for your application
ENV PYTHONPATH=/code

# --- Command to start the Streamlit application ---
# Uncomment the following line to use UV to run the application instead of Python
# CMD ["uv", "run", "launcher.py"]

# Default: Use Python to run the application
CMD ["python", "launcher.py"]
