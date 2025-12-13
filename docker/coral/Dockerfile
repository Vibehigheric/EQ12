FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Add Coral repo
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/coral-edgetpu.gpg \
    && echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

# Install Coral libraries
RUN apt-get update && apt-get install -y \
    libedgetpu1-std \
    && rm -rf /var/lib/apt/lists/*

# Install Python bindings via pip
RUN pip install "numpy<2.0" \
    && pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0

# Copy test script
COPY coral_test.py .

CMD ["python3", "coral_test.py"]
