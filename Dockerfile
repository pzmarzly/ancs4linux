FROM python:3.7
RUN apt-get update && apt-get install -y libdbus-1-dev libgirepository1.0-dev

WORKDIR /src
COPY . .
RUN pip install . --use-feature=in-tree-build
