APP_NAME = lambda

IMAGE_NAME = ${APP_NAME}

CUR_DIR = $(shell echo "${PWD}")

# location of Dockerfiles
DOCKER_FILE_DIR=docker
DOCKERFILE="${DOCKER_FILE_DIR}/Dockerfile"

#################################
# Install targets
#################################


_build:
	docker build \
	--file=${DOCKERFILE} \
	--tag=${IMAGE_NAME}:latest ${DOCKER_FILE_DIR}/ \


test: clean _build
	docker run  -t \
	--name ${APP_NAME}-unit-tests \
	--volume ${CUR_DIR}:/io \
	${IMAGE_NAME}:latest \
	/bin/bash -c "cd io; python3 -m pip install -r /lambda/package-requirements.txt; python3 -m pytest awslambda/test" \

clean:
	 docker rmi ${IMAGE_NAME}:latest  || true

deploy:_build
	docker run --rm \
	--name ${APP_NAME}-deploy \
	--volume ${CUR_DIR}:/io \
    ${IMAGE_NAME}:latest \
    bash /lambda/packager.sh \

.PHONY: deploy _build clean