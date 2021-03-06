APP_NAME = lambda
FUNCTION_NAME = rekogFaceAnon
BUCKET_NAME = pez-rekog-image1

IMAGE_NAME = ${APP_NAME}

CUR_DIR = $(shell echo "${PWD}")
BUILD_DIR = deployment
LOCAL_FONT_DIR = /io/assets/fonts

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
	docker run  --rm \
	--name ${APP_NAME}-unit-tests \
	--volume ${CUR_DIR}:/io \
	${IMAGE_NAME}:latest \
	/bin/bash -c "cd io; python3 -m pip install -r /lambda/package-requirements.txt; python3 -m pytest awslambda/test" \

clean:
	@docker rmi -f ${IMAGE_NAME}:latest  || true
	rm -f ${BUILD_DIR}/lambda.zip

upload:
	cd ${BUILD_DIR}
	aws lambda update-function-code \
    --function-name ${FUNCTION_NAME} \
    --zip-file fileb:///${CUR_DIR}/${BUILD_DIR}/lambda.zip \
    --output json \
    --no-paginate >${BUILD_DIR}/deploy-receipt.json

deploy:clean test package upload

local: clean _build
	docker run  --rm \
	--name ${APP_NAME}-local \
	--volume ${CUR_DIR}:/io \
	${IMAGE_NAME}:latest \
	/bin/bash -c "export TARGET_BUCKET=${BUCKET_NAME}; \
	export FONT_DIR=${LOCAL_FONT_DIR}; \
	python3 -m pip install -r /lambda/package-requirements.txt; \
	cd io/awslambda/src; \
	python3 local_output.py " \

package:
	docker run --rm \
	--name ${APP_NAME}-deploy \
	--volume ${CUR_DIR}:/io \
    ${IMAGE_NAME}:latest \
    bash /lambda/packager.sh \

.PHONY: deploy _build clean upload package