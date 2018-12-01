DOCKER   := docker
TAG_BASE := blbridges96/project

all: api

.PHONY: api
api:
	$(DOCKER) build -t $(TAG_BASE)-api -f Dockerfile.api .
