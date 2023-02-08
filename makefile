.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

black: ## black formatting
	black .

mlflow:
	mlflow ui

clean:
	pre-commit run --all-files



build:
	sam build --use-container -t template.yaml

local:
	sam local start-api

deploy:
	sam deploy \
	--stack-name docker-sam-app \
	--s3-bucket portfolio-on-lambda-2999-v3 \
	--capabilities CAPABILITY_IAM \
	--resolve-image-repos
