# pull official base image
FROM python:3.12-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
  apt-get install -y \
  netcat-openbsd gettext

# install dependencies
RUN pip install --no-cache --upgrade uv


RUN useradd -ms /bin/bash app
# create the appropriate directories

ENV HOME=/home/app
ENV APP_HOME=/home/app/web

RUN mkdir -p $APP_HOME /static /media /uploads/tmp /uploads/final \
  && chown -R app:app /static /media /uploads ${APP_HOME}
WORKDIR $APP_HOME

USER app

COPY ./pyproject.toml ./uv.lock ./
RUN uv venv --clear && uv sync --no-dev --frozen

ENV PATH="/home/app/web/.venv/bin:$PATH"

# copy project
COPY --chown=app:app . $APP_HOME


# change to the app user

RUN python manage.py compilemessages && python manage.py collectstatic

ENTRYPOINT ["/home/app/web/entrypoint.sh"]

CMD gunicorn core.wsgi:application --bind 0.0.0.0:8000
