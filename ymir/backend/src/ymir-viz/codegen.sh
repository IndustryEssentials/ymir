CODE_FOLDER=$(
	cd "$(dirname "$0")"
	pwd
)

rm -rf ./codegen_output/*
mkdir -p ./codegen_output/
echo "$CODE_FOLDER"

docker run --user $(id -u ${USER}):$(id -g ${USER}) --rm -v ${CODE_FOLDER}:/local swaggerapi/swagger-codegen-cli-v3 generate \
-i /local/doc/ymir_viz_API.yaml \
--model-package swagger_models \
-l python-flask \
-o /local/codegen_output

sed -i "s/swagger_server/src/g" $(grep swagger_server -rl ${CODE_FOLDER}/codegen_output/*)

cp -rf ${CODE_FOLDER}/codegen_output/swagger_server/swagger_models ${CODE_FOLDER}/src/
cp -rf ${CODE_FOLDER}/codegen_output/swagger_server/swagger ${CODE_FOLDER}/src/
rm -rf ./codegen_output
