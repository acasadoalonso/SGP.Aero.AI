#!make

CONTAINER_NAME := sgpmcp
IMAGE_NAME     := sgpmcp

build:
	docker build --no-cache=false -t ${IMAGE_NAME} .

exec:
	docker stop ${CONTAINER_NAME}
	docker rm   ${CONTAINER_NAME}
	docker run --name ${CONTAINER_NAME}  --restart unless-stopped  -d -p 9010:9010 ${IMAGE_NAME} 

clean:
	docker stop ${CONTAINER_NAME} 
	docker rm   ${CONTAINER_NAME} 
	docker rmi  ${IMAGE_NAME} 
	docker images

