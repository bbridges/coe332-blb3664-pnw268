DOCKER   := docker
TAG_BASE := blbridges96/project

all: api worker

.PHONY: api
api:
	$(DOCKER) build -t $(TAG_BASE)-api -f Dockerfile.api .

.PHONY: worker
worker:
	$(DOCKER) build -t $(TAG_BASE)-worker -f Dockerfile.worker .
