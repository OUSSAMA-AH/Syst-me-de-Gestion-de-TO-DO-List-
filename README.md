# Systeme_de_Gestion_de_TO-DO_List
# Nom du fichier: makefile
# Assurez-vous que ce fichier se trouve dans le même répertoire que votre script todo_list.py et requirements.txt

# Nom de l'environnement virtuel
VENV_DIR = venv

# Commandes pour Python et pip
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip

# Créer l'environnement virtuel
venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Installer les dépendances
install: venv
	$(PIP) install -r requirements.txt

# Activer l'environnement virtuel
activate:
	@echo "Pour activer l'environnement virtuel, exécutez :"
	@echo "source $(VENV_DIR)/bin/activate"

# Exécuter le script avec des arguments
run: install
	$(VENV_DIR)/bin/python task_manager.py tasks.json log.txt

# Nettoyer les fichiers générés
clean:
	rm -rf $(VENV_DIR)
	find . -type f -name '*.pyc' -delete
	find . -type d -name 'pycache' -exec rm -rf {} +

# Afficher l'aide
help:
	@echo "Commandes disponibles:"
	@echo "  make          : Crée l'environnement virtuel et installe les dépendances"
	@echo "  make run      : Exécute le script Python avec des arguments"
	@echo "  make install  : Installe les dépendances dans l'environnement virtuel"
	@echo "  make activate : Affiche la commande pour activer l'environnement virtuel"
	@echo "  make clean    : Supprime l'environnement virtuel et les fichiers temporaires"
	@echo "  make help     : Affiche cette aide"

.PHONY: venv install activate run clean help
