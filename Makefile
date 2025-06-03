# Makefile for Django project

.PHONY: run migrate createsuperuser shell

run:
	docker compose up --build

migrate:
	docker compose exec backend python manage.py migrate

createsuperuser:
	docker compose exec backend python manage.py createsuperuser

shell:
	docker compose run --rm backend python manage.py shell
