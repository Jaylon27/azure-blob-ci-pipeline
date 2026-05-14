# Use the slim variant instead of the full python:3.12 image. The full image
# ships build tools and OS packages we don't need at runtime, which inflates
# size and increases the attack surface.
FROM python:3.12-slim

# PYTHONDONTWRITEBYTECODE: skip writing .pyc files inside the image.
# PYTHONUNBUFFERED: stream stdout/stderr immediately so logs aren't lost on
# crash and CI tails work in real time.
# PIP_* flags: skip the pip cache (smaller image) and the pip self-version
# check (faster, no outbound call during build).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Create the runtime user now; COPY and pip install still run as root below.
RUN adduser --system --no-create-home --group app

# Copy requirements first and install them in their own layer. Source code
# changes far more often than dependencies, so this lets Docker reuse the
# cached dependency layer on subsequent builds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application source. Tests, CI metadata, and local caches are
# excluded via .dockerignore so they never enter the image.
COPY src/ ./src/

# Drop privileges before the container starts. An unprivileged user limits the blast radius if the
# process is compromised.
USER app

CMD ["python", "/app/src/adls_client.py"]
