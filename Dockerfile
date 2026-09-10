FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wget curl git python3 python3-pip \
    nodejs npm neofetch vim nano htop build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --tries=3 --timeout=30 -qO /bin/ttyd \
    https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 && \
    chmod +x /bin/ttyd

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app.py .

RUN echo "neofetch" >> /root/.bashrc && \
    echo "cd /root" >> /root/.bashrc

EXPOSE 8080

CMD ["python3", "/app/app.py"]
