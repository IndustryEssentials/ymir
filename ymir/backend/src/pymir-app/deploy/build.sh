docker-compose -p ymir_backend down -v --remove-orphans
docker-compose -p ymir_backend -f docker-compose.yml -f docker-compose.prod.yml up --build -d
