FROM --platform=linux/amd64 python:3.9
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get -y install gcc
RUN apt-get -y install curl

COPY . .

# To print out stdout to docker logs
ENV PYTHONUNBUFFERED=1

# Install ODBC Driver Version 18 and Debian Version 10
ENV DOCKER_CONTENT_TRUST 1
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=DontWarn

ENV DEBIAN_FRONTEND noninteractive

ENV ACCEPT_EULA=Y
RUN apt-get update -y && apt-get update \
  && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev

RUN apt-get install -y curl apt-transport-https

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list 

RUN apt-get update 
RUN apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql18 mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bash_profile 
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc

RUN apt-get -y clean


# RUN apt-get update && \
#     apt-get install --yes --no-install-recommends \
#         apt-transport-https \
#         curl \
#         gnupg \
#         unixodbc-dev && \
#     curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
#     curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
#     apt-get update && \
#     ACCEPT_EULA=Y apt-get install --yes --no-install-recommends msodbcsql17 && \
#     apt-get install -y r-base && \
#     R -e "install.packages('odbc')" && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/* && \
#     rm -rf /tmp/*


RUN pip3 install -r requirements.txt
COPY . .
ENV FLASK_APP=betula.py
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--debug"]