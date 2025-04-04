FROM python:3.9.21-bookworm

WORKDIR /app

# Deps
RUN apt update && \
    apt install -y curl apt-transport-https software-properties-common gnupg2 lsb-release

# /Sqlserver
RUN curl -sSL -O https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update

ENV DEBIAN_FRONTEND=noninteractive
ENV ACCEPT_EULA=Y
RUN apt install -y msodbcsql17 unixodbc-dev
# \Sqlserver

# /Oracle
RUN apt install -y libaio1 wget unzip && \
    mkdir -p /opt/oracle

RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip -O /opt/oracle/instantclient.zip && \
    unzip /opt/oracle/instantclient.zip -d /opt/oracle && \
    rm /opt/oracle/instantclient.zip

ENV ORACLE_HOME=/opt/oracle/instantclient_23_7
ENV LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
ENV PATH=$ORACLE_HOME:$PATH
# \Oracle

COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]