# Raccourcis Scribe (self-host)
.PHONY: install start stop logs pull-model restart ps

install:        ## Installe tout et lance (Docker + GPU + modèles)
	sudo bash install.sh

start:          ## Démarre la stack
	docker compose up -d --build

stop:           ## Arrête la stack
	docker compose down

restart: stop start

logs:           ## Affiche les logs en continu
	docker compose logs -f

ps:             ## État des conteneurs
	docker compose ps

pull-model:     ## (Re)télécharge le modèle LLM Qwen
	docker compose exec ollama ollama pull qwen2.5:7b-instruct
