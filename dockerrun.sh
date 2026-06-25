docker stop sgpmcp
docker rm sgpmcp
docker run --name sgpmcp --restart unless-stopped  -d -p 9010:9010 sgpmcp
