# ---------- Stage 1: Base image with Poetry ----------
FROM python:3.11-slim AS base

# Make sure that pip up-to-date is and install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# ---------- Stage 2: Builder ---------- (Set-up project environment)
FROM base AS builder
WORKDIR /build

# Prevent Poetry from making a virtual environment (install everything in the global Python environment of the container)
RUN poetry config virtualenvs.create false

# Copy only the toml and lock files to make use of the cache
COPY pyproject.toml poetry.lock .

# Install dependencies in the global Python environment
RUN poetry install --no-interaction --no-root

# ---------- Stage 3: Final image ----------
FROM python:3.11-slim AS final

# Copy dependencies from builder
# copy installed libraries
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# copy executables (e.g., uvicorn, poetry, pip)
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the project files
COPY ./app /app
COPY ./cptlib /cptlib

# Expose port for uvicorn (only metadata)
EXPOSE 8000

# Start the app with Python
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
