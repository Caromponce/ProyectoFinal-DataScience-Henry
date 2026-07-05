install:
	pip install -r requirements.txt

run:
	uvicorn api.main:app --reload

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose down
	docker compose up --build