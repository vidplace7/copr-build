FROM quay.io/centos/centos:stream10

# Install COPR CLI
RUN dnf config-manager --set-enabled crb \
    && dnf install -y epel-release \
    && dnf install -y copr-cli

COPY entrypoint.py /entrypoint.py
ENTRYPOINT [ "/entrypoint.py" ]
