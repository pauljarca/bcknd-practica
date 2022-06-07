FROM python:3.10

WORKDIR /app/server

RUN adduser -uid 101 --disabled-login --disabled-password --gid 101  django

# Set the time zone inside the container
RUN apt-get install tzdata \
    && cp /usr/share/zoneinfo/Europe/Bucharest /etc/localtime \
    && echo "Europe/Bucharest" >  /etc/timezone

COPY requirements.txt ./
RUN set -ex \
    && pip install --upgrade pip \
    && pip install --no-cache -r requirements.txt

COPY django-entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/django-entrypoint.sh
ENTRYPOINT [ "/usr/bin/django-entrypoint.sh" ]
ENV DJANGO_SETTINGS_MODULE=practica.settings.production
EXPOSE 8000

COPY . .
RUN mkdir -p logs

RUN  set -ex; \
     curl -o /usr/local/bin/su-exec.c https://raw.githubusercontent.com/ncopa/su-exec/master/su-exec.c; \
     fetch_deps='gcc libc-dev'; \
     apt-get update; \
     apt-get install -y --no-install-recommends $fetch_deps; \
     rm -rf /var/lib/apt/lists/*; \
     gcc -Wall \
         /usr/local/bin/su-exec.c -o/usr/local/bin/su-exec; \
     chown root:root /usr/local/bin/su-exec; \
     chmod 0755 /usr/local/bin/su-exec; \
     rm /usr/local/bin/su-exec.c; \
     \
     apt-get purge -y --auto-remove $fetch_deps
