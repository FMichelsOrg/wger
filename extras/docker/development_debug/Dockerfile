#
# Docker image for wger development
#
# Please consult the README for usage
#
# Note: you MUST build this image from the project's root!
# docker build -f extras/docker/development/Dockerfile --tag wger/server .
#
# Run the container:
# docker run -ti -v /path/to/this/checkout:/home/wger/src --name wger.dev --publish 8000:8000 wger/server

##########
# Builder
##########
FROM wger/server:latest
RUN pip install debugpy
#COPY entrypoint.sh /home/wger/entrypoint.sh
