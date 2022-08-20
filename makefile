.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

black: ## black formatting
	black .

push-docker:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 398212703914.dkr.ecr.us-east-1.amazonaws.com
	docker build -t songtranslator .
	docker tag songtranslator:latest 398212703914.dkr.ecr.us-east-1.amazonaws.com/songtranslator:latest
	docker push 398212703914.dkr.ecr.us-east-1.amazonaws.com/songtranslator:latest
