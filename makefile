.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

black: ## black formatting
	black .


test:
	python -m pytest

mlflow:
	mlflow ui

docs:
	pdoc music_flow -o ./docs

lint:
	ruff .

clean:
	pre-commit run --all-files

build:
	sam build --use-container -t template.yaml --debug

local: build
	sam local start-api --debug --port 5858

validate:
	sam validate --debug

sync: validate build
	sam sync --stack-name musicflow-sam-app --watch

deploy: build
	sam deploy \
	--stack-name musicflow-sam-app \
	--s3-bucket portfolio-on-lambda-2999-v3 \
	--capabilities CAPABILITY_NAMED_IAM \
	--resolve-image-repos \
	--debug

ci-deploy:
	sam deploy --stack-name ${{env.STACK_NAME}} --s3-bucket ${{env.S3_BUCKET}} --capabilities CAPABILITY_IAM --resolve-image-repos --no-confirm-changeset --no-fail-on-empty-changeset


ecr-login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 398212703914.dkr.ecr.us-east-1.amazonaws.com


delete:
	sam delete --stack-name musicflow-sam-app
