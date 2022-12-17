.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

black: ## black formatting
	black .

mlflow:
	mlflow ui
