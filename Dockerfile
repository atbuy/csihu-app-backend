FROM python:3.11-alpine AS python

# Python configurations
ENV PYTHONBUFFERED=true
WORKDIR /app

RUN apk update


# Install package in second stage
FROM python as build

RUN apk add --no-cache gcc musl-dev curl libffi-dev

# Copy source code
COPY . /app
WORKDIR /app

# Poetry configuration
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:${PATH}"

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools wheel && \
    # Install poetry
    pip install poetry && \
    # Install dependencies from poetry lock file
    poetry install --no-dev --no-interaction --no-ansi -vvv


# Run app in third stage
FROM python AS runtime

# Add poetry virtual environment to PATH
ENV PATH="/app/.venv/bin:${PATH}"

# Copy source
COPY --from=build /app /app
WORKDIR /app

ENTRYPOINT [ "uvicorn", "cab.main:app", "--host", "0.0.0.0", "--port", "8001" ]
