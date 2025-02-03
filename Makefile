SHELL := /bin/bash

#setup:
#	@echo "Initializing the testing environment"
#	@docker compose up -d --build
#
#setup_uc_only:
#	@echo "Initializing the UC environment only"
#	@docker compose up -d --build uc-server uc-ui minio
#
#prepare_dataset:
#	@echo "Preparing the dataset with table format=$(table_format) for the spark job"
#	@docker exec -it uc-spark-master spark-submit \
#		--master spark://uc-spark-master:7077 \
#		/app/prepare_dataset.py --table-format=$(table_format);
#
#enable_uniform:
#	@echo "Enabling uniform distribution"
#	@docker exec -it uc-spark-master spark-submit \
#		--master spark://uc-spark-master:7077 \
#		/app/enable_uniform.py --schema-name=$(schema_name) --table-name=$(table_name);
#
#clean:
#	@echo "Clean up the spark environment"
#	@docker-compose down --remove-orphans

test:
	@echo "Running tests"
	@uv run pytest tests/ -v -s --log-cli-level=INFO