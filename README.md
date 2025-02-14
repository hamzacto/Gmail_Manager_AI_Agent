# IntelliLettre

## Présentation

Ce projet est une application web composée d'un backend et d'un frontend.  
Le backend est développé avec FastAPI et fournit plusieurs services, notamment :  
- L'authentification et la gestion des utilisateurs.  
- La récupération des emails récents via une intégration avec Gmail (via le service GmailService).  
- Le traitement de commandes (par exemple, « envoyer un email à john@example.com ») en utilisant un service d'interprétation IA (AIService).  
- Une vérification de l'état de santé de l'application via des endpoints dédiés.

Le frontend est une application Node.js (construite avec Vite) qui permet d'interagir avec ces services.

## Fonctionnalités

- **Authentification** : Gère la connexion et l’identification des utilisateurs via les endpoints d’authentification.
- **Gestion des emails** : 
  - Récupération des emails récents.
  - Traitement de commandes textuelles pour envoyer des emails ou réaliser d’autres opérations.
- **Intégration IA** : Utilisation d’un service d’IA pour interpréter et exécuter des commandes.
- **Health Check** : Endpoint de vérification de l’état du système pour s’assurer que toutes les composantes sont opérationnelles.

## Structure du projet

- **backend/**  
  Contient l’application FastAPI, la configuration du projet, les services (GmailService, AIService) et les routes (auth, emails).
  
- **frontend/**  
  Contient l’application frontend qui communique avec le backend.

- **docker-compose.yml**  
  Fichier de configuration pour exécuter l’ensemble des services (backend et frontend) dans des conteneurs Docker.

- **Makefile**  
  Fichier pour simplifier l’installation, le démarrage et les tests du projet.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et [Docker‑Compose](https://docs.docker.com/compose/install/)
- (Optionnel) Si vous désirez exécuter les commandes localement sans Docker :  
  - Python 3.11 ou supérieur  
  - Node.js (pour le frontend)

## Installation

### Installation manuelle (localement sans Docker)

1. **Backend**  
   Placez-vous dans le répertoire `backend` et installez les dépendances :
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend**  
   Placez-vous dans le répertoire `frontend` et installez les dépendances Node :
   ```bash
   cd frontend
   npm install
   ```

### Installation avec Docker‑Compose

Le projet est fourni avec un fichier `docker-compose.yml` qui définit le service backend et le service frontend.  
Celui-ci configure également l’environnement (variables d’environnement, volumes, etc.).

## Construction et exécution

### Construction et exécution via Docker‑Compose

Pour construire et lancer l’application, exécutez la commande suivante à la racine du projet :

```bash
docker-compose up --build
```

Une fois lancés :

- Le backend est accessible à l’adresse : [http://localhost:8000](http://localhost:8000)
- Le frontend est accessible à l’adresse : [http://localhost:5173](http://localhost:5173)

### Exécution locale (sans Docker)

1. **Lancer le backend**  
   Depuis le répertoire `backend`, vous pouvez lancer l’application avec Uvicorn (ou en utilisant le Makefile) :
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Ou avec la commande :
   ```bash
   make backend
   ```

2. **Lancer le frontend**  
   Depuis le répertoire `frontend`, lancez le serveur de développement :
   ```bash
   cd frontend
   npm run dev
   ```

## Tests

### Tests du backend

Les tests unitaires sont gérés avec [pytest](https://docs.pytest.org/).  
Pour exécuter les tests, lancez la commande suivante depuis le répertoire racine ou dans `backend` :

```bash
make backend_test
```

ou directement :

```bash
cd backend
pytest
```

## Utilisation de l'API

Quelques endpoints disponibles :

- **Récupérer les emails récents**  
  `GET /api/emails/recent?limit=10`
  
- **Traitement d'une commande**  
  `POST /api/emails/process-command`  
  Corps de la requête (JSON) :
  ```json
  {
    "command": "Envoyer un email à john@example.com"
  }
  ```

- **Health Check**  
  `GET /health` ou `GET /health_check`

## Personnalisation et configuration

- Le fichier de configuration principal se trouve dans `backend/app/core/config.py`.  
- Les variables d'environnement (comme `GROQ_API_KEY`, `SECRET_KEY`, `DEBUG`, etc.) sont définies dans le fichier `docker-compose.yml` et peuvent également être gérées via un fichier `.env` si besoin.
