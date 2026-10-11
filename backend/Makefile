runserver:
	python manage.py runserver

celery:
	celery -A src worker -l INFO

beat:
	celery -A src beat -l INFO

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

migboth:
	make migrations & \
	make migrate

superuser:
	python manage.py createsuperuser

# =========  SPECIAL COMMANDS ============

create-ent:
	python manage.py create_ent --dep 1 --part 2

create-emp:
	python manage.py create_employees --id 1 --count 1

create-events:
	python manage.py create_access_control --id 1

shell:
	python manage.py shell

# ===================== ============================

remove:
	rm -rf db.sqlite3
create:
	make remove
	make migboth

init:
	make create
	make superuser
	make create-ent dep=1 part=2
	make create-emp id=1 count=1
	make create-events id=1
