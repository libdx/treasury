APP = web
PROJECT = project
TESTS = $(PROJECT)/tests

.PHONY: clean

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

up:
	docker-compose up --detach

up-build:
	docker-compose up --build --detach

logs:
	docker-compose logs $(APP)

exec:
	docker-compose exec $(APP) $(CMD)

manage:
	docker-compose exec $(APP) python manage.py $(CMD)

manage-help:
	docker-compose exec $(APP) python manage.py --help

migrate:
	docker-compose exec $(APP) python manage.py migrate

shell:
	docker-compose exec $(APP) python manage.py shell

install:
	docker-compose exec $(APP) sh -c \
		"pip install -r requirements.txt && pip install -r requirements-dev.txt"

test:
	docker-compose exec $(APP) \
		pytest $(TESTS) -p no:warnings $(FLAGS)

coverage:
	docker-compose exec $(APP) \
		pytest $(TESTS) -p no:warnings --cov=$(PROJECT)

lint:
	docker-compose exec $(APP) flake8 $(PROJECT)

fix:
	docker-compose exec $(APP) sh -c \
		"black $(PROJECT) && isort $(PROJECT)"

fix-ownership:
	sudo chown -R $USER:$USER $(PROJECT)
