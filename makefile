.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

init: ## create all folders
	# TODO

black: ## black formatting
	black .

mlflow:
	mlflow ui

clean:
	pre-commit run --all-files

build:
	sam build --use-container -t template.yaml --debug

local:
	sam local start-api --debug --port 5858

deploy:
	sam deploy \
	--stack-name musicflow-sam-app \
	--s3-bucket portfolio-on-lambda-2999-v3 \
	--capabilities CAPABILITY_IAM \
	--resolve-image-repos --debug

ci-deploy:
	sam deploy --stack-name ${{env.STACK_NAME}} --s3-bucket ${{env.S3_BUCKET}} --capabilities CAPABILITY_IAM --resolve-image-repos --no-confirm-changeset --no-fail-on-empty-changeset 
