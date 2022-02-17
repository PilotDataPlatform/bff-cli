FROM python:3.8-buster

WORKDIR /usr/src/app

ARG pip_username
ARG pip_password

ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && apt-get update && \
apt-get install -y vim-tiny less && ln -s /usr/bin/vim.tiny /usr/bin/vim && rm -rf /var/lib/apt/lists/*

COPY . .
RUN PIP_USERNAME=$pip_username PIP_PASSWORD=$pip_password pip install --no-cache-dir -r requirements.txt -r internal_requirements.txt && chmod +x gunicorn_starter.sh

CMD ["./gunicorn_starter.sh"]
