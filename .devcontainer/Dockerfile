# Base Image for Python Development
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    iptables \
    sudo \
    docker.io \
    git

# Install Tailscale
RUN curl -fsSL https://tailscale.com/install.sh | sh

# Create the vscode user if it doesn't exist
RUN id -u vscode &>/dev/null || useradd -m -s /bin/bash vscode

# Add vscode user to sudoers
RUN usermod -aG sudo vscode && \
    echo 'vscode ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/vscode

# Ensure docker.sock is accessible
RUN chmod 666 /var/run/docker.sock || true

# Expose Tailscale port
EXPOSE 41641/udp

# Copy dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Set permissions for vscode user
RUN chown -R vscode:vscode /home/vscode

# Switch to vscode user
USER vscode

# Default command
CMD ["bash", "-c", "sudo service docker start && tailscaled & tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=devcontainer && sleep infinity"]
