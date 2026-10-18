# M-Motors — Vente, location et financement automobile

M-Motors est une application web dédiée à la vente, à la location et au financement de véhicules. Elle permet aux visiteurs de consulter un catalogue automobile et aux utilisateurs de réaliser différentes démarches en ligne, depuis la consultation d'une offre jusqu'au suivi de leur dossier.

Le projet repose sur une architecture modulaire fondée sur les principes de la **Clean Architecture**, avec un frontend React, une API REST FastAPI et une infrastructure conteneurisée avec Docker.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture technique](#architecture-technique)
- [Technologies utilisées](#technologies-utilisées)
- [Organisation des dépôts](#organisation-des-dépôts)
- [Installation en local](#installation-en-local)
- [Configuration des services externes](#configuration-des-services-externes)
- [Configuration générale](#configuration-générale)
- [Lancement de l'application](#lancement-de-lapplication)
- [Tests](#tests)
- [Déploiement en production](#déploiement-en-production)

## Fonctionnalités

Pour consulter la liste détaillée des fonctionnalités, reportez-vous au fichier `documentation_utilisateur.pdf`, disponible à la racine du dépôt backend.

## Architecture technique

L'application sépare l'interface utilisateur, la logique applicative, le domaine métier et les infrastructures techniques.

En production, Nginx sert le frontend et transmet les requêtes API aux instances FastAPI. Les instances partagent les mêmes services de données et de stockage.

```text
                         UTILISATEUR
                              |
                              v
                         NGINX (production)
                         /               \
                        v                 v
                 FRONTEND REACT       API REST
                                          |
                                  +-------+-------+
                                  |               |
                                  v               v
                              FASTAPI 1       FASTAPI 2
                                  |               |
                                  +-------+-------+
                                          |
                       +------------------+------------------+
                       |                  |                  |
                       v                  v                  v
                  PostgreSQL            Redis               MinIO
                                          |
                                          v
                                      RQ Worker

                       Services externes : Stripe, Brevo
```

Ce schéma représente l'architecture de production prévue avec deux instances FastAPI. Le nombre d'instances effectivement lancées dépend de la configuration de déploiement.

Le **RQ Worker communique avec Redis** pour récupérer les tâches asynchrones. MinIO est utilisé pour le stockage des fichiers et des images.

### Principes d'architecture

Le backend applique les principes de la Clean Architecture :

- **Domaine** : entités, règles métier et objets du domaine.
- **Application** : cas d'utilisation qui orchestrent les traitements.
- **Infrastructure** : persistance, dépôts SQLAlchemy, services externes et mécanismes techniques.
- **API** : routes FastAPI, validation des entrées et exposition des fonctionnalités.

Les cas d'utilisation sont ainsi séparés des détails techniques de persistance et de communication avec les services externes.

## Technologies utilisées

| Domaine                       | Technologie            | Rôle                                               |
| ----------------------------- | ---------------------- | -------------------------------------------------- |
| Frontend                      | React                  | Interface utilisateur                              |
| Backend                       | Python, FastAPI        | API REST et logique applicative                    |
| Base de données               | PostgreSQL             | Stockage des données                               |
| ORM et migrations             | SQLAlchemy, Alembic    | Accès aux données et gestion du schéma             |
| Files de tâches et messagerie | Redis                  | Files d'attente et Pub/Sub                         |
| Tâches asynchrones            | RQ Worker              | Exécution des tâches en arrière-plan               |
| Stockage de fichiers          | MinIO                  | Stockage des fichiers et images                    |
| Paiement                      | Stripe                 | Gestion des paiements                              |
| Emails transactionnels        | Brevo via SMTP         | Envoi des emails                                   |
| Suivi des erreurs             | Sentry                 | Collecte des erreurs, si activée                   |
| Conteneurisation              | Docker, Docker Compose | Environnements de développement et de déploiement  |
| Serveur web                   | Nginx                  | Distribution du frontend et proxy des requêtes API |

## Organisation des dépôts

Le backend et le frontend sont organisés dans deux dépôts distincts :

- **Backend** : [Leila-33/backendmmotors](https://github.com/Leila-33/backendmmotors)
- **Frontend** : [Leila-33/frontend](https://github.com/Leila-33/frontend)

## Installation en local

### Prérequis

Installer les outils suivants :

- Git
- Docker et Docker Compose
- Node.js et npm pour le frontend
- Stripe CLI pour tester les webhooks Stripe en local

### 1. Récupérer les dépôts

```bash
git clone https://github.com/Leila-33/backendmmotors.git
git clone https://github.com/Leila-33/frontend.git
```

### 2. Configurer le backend

Se placer dans le dossier du backend :

```bash
cd backendmmotors
```

Créer le fichier d'environnement local à partir du modèle `.env.example` :

```bash
cp .env.example .env
```

Sous Windows PowerShell, utiliser :

```powershell
Copy-Item .env.example .env
```

Renseigner dans `.env` les variables requises par le projet. Ne publiez jamais ce fichier ni ses secrets dans le dépôt Git.

### 3. Démarrer les services Docker

Depuis le dossier contenant le fichier `docker-compose.yml` :

```bash
docker compose up --build -d
```

Vérifier l'état des conteneurs :

```bash
docker compose ps
```

Consulter les journaux en cas de problème :

```bash
docker compose logs -f
```

### 4. Appliquer les migrations de base de données

Une fois les services API et PostgreSQL démarrés :

```bash
docker compose exec api alembic upgrade head
```

Cette commande applique les migrations Alembic disponibles dans le projet. Elle doit être exécutée dans l'environnement où le service `api` et sa configuration sont accessibles.

### 5. Initialiser les options de location

Si le script `seed_options.py` est présent à la racine du backend et correspond à la version du projet, exécuter :

```bash
docker compose exec api python seed_options.py
```

### 6. Créer le bucket MinIO

Ouvrir la console MinIO à l'adresse et au port configurés dans `docker-compose.yml`, puis se connecter avec les identifiants définis dans `.env`.

Créer le bucket indiqué par la variable `S3_BUCKET`, par exemple `vehicles`, sauf si l'application le crée automatiquement.

### 7. Installer et lancer le frontend

Dans un autre terminal :

```bash
cd ../frontend
npm install
npm start
```

Les commandes exactes peuvent varier selon les scripts définis dans le fichier `package.json` du frontend.

## Configuration des services externes

Certaines fonctionnalités nécessitent des services externes. Configure uniquement les services utilisés par la version du projet que tu exécutes.

### 1. Stripe — Paiements de test

Stripe permet de tester les paiements sans utiliser de véritables transactions.

1. Créer un compte sur [Stripe](https://stripe.com/).
2. Activer le mode test dans le tableau de bord Stripe.
3. Récupérer les clés API de test.
4. Renseigner les variables suivantes dans `.env` :

```dotenv
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

- `STRIPE_SECRET_KEY` : clé secrète de test utilisée par le backend.
- `STRIPE_PUBLIC_KEY` : clé publique de test, généralement utilisée par le frontend.
- `STRIPE_WEBHOOK_SECRET` : secret utilisé pour vérifier la signature des événements reçus.

Ne publiez jamais les clés secrètes dans le dépôt Git.

#### Configurer le webhook Stripe en local

Le gestionnaire de webhook du backend traite les événements suivants :

| Événement Stripe             | Utilisation                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| `checkout.session.completed` | Traitement du paiement de l'acompte                          |
| `invoice.created`            | Traitement de la création d'une facture liée à un abonnement |
| `invoice.paid`               | Traitement du paiement d'une mensualité                      |
| `invoice.payment_failed`     | Traitement de l'échec du paiement d'une mensualité           |

1. Installer [Stripe CLI](https://docs.stripe.com/stripe-cli).
2. Se connecter à Stripe :

```bash
stripe login
```

3. Transmettre les événements à l'URL locale du webhook :

```bash
stripe listen --forward-to localhost:8000/api/.../webhook
```

Remplacer `/api/.../webhook` par le chemin réel du webhook dans l'application.

Stripe CLI affiche un secret commençant par `whsec_`. Renseigner cette valeur dans `STRIPE_WEBHOOK_SECRET` pour les tests locaux.

En production, créer un endpoint webhook dans le tableau de bord Stripe et sélectionner les quatre événements listés ci-dessus. Utiliser ensuite le secret associé à cet endpoint. Le secret de production est différent de celui fourni par Stripe CLI.

### 2. Brevo — Emails transactionnels

Brevo permet d'envoyer les emails transactionnels, notamment les emails de vérification de compte et de réinitialisation du mot de passe.

#### Créer un compte Brevo

1. Créer un compte sur [Brevo](https://www.brevo.com/).
2. Configurer et vérifier une adresse d'expéditeur.
3. Récupérer les identifiants SMTP dans les paramètres du compte.

#### Configurer les variables d'environnement

Renseigner les variables suivantes dans `.env` :

```dotenv
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=your_smtp_login
SMTP_PASSWORD=your_smtp_key
SMTP_FROM_EMAIL=your_verified_sender@example.com
```

- `SMTP_HOST` : serveur SMTP de Brevo.
- `SMTP_PORT` : port SMTP utilisé, ici 587.
- `SMTP_USER` : identifiant SMTP fourni par Brevo.
- `SMTP_PASSWORD` : clé SMTP fournie par Brevo, et non la clé API.
- `SMTP_FROM_EMAIL` : adresse d'expéditeur vérifiée dans Brevo.

Cette configuration peut être utilisée en local et en production. Les identifiants doivent être configurés séparément dans chaque environnement.

**Attention :** les emails envoyés depuis l'environnement local peuvent être réellement transmis aux destinataires. Utiliser une adresse de test contrôlée pendant le développement.

### 3. Sentry — Suivi des erreurs

Sentry permet de collecter et de suivre les erreurs de l'application. Son utilisation est facultative si le backend accepte l'absence de DSN.

1. Créer un compte sur [Sentry](https://sentry.io/).
2. Créer un projet adapté au backend Python/FastAPI.
3. Récupérer le DSN du projet.
4. Renseigner les variables suivantes dans `.env` :

```dotenv
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1
```

Vérifier que le code du backend tolère un `SENTRY_DSN` vide avant de lancer l'application sans configuration Sentry.

## Configuration générale

Le backend utilise des variables d'environnement pour les paramètres de connexion et les secrets. Le fichier `.env.example` doit servir de modèle. Les valeurs réelles doivent être définies dans `.env` en local ou dans l'environnement sécurisé de déploiement.

| Catégorie        | Utilisation                              |
| ---------------- | ---------------------------------------- |
| PostgreSQL       | Connexion à la base de données           |
| Redis            | Files de tâches et Pub/Sub               |
| MinIO            | Endpoint, bucket et identifiants d'accès |
| Authentification | Clés et paramètres des jetons            |
| Stripe           | Clés API et configuration du webhook     |
| E-mails          | Paramètres SMTP de Brevo                 |
| Sentry           | DSN et environnement, si activé          |
| Frontend         | URL du frontend et URL de l'API backend  |

Ne commitez jamais le fichier `.env`. Vérifiez qu'il est ignoré par Git et que `.env.example` ne contient aucun secret réel.

## Lancement de l'application

Une fois les services démarrés, les points d'accès dépendent de la configuration locale :

- **Frontend React** : généralement `http://localhost:3000`.
- **API FastAPI** : généralement `http://localhost:8000`.
- **Documentation interactive** : généralement `http://localhost:8000/docs`, si OpenAPI est activé.
- **MinIO** : l'API et la console sont accessibles selon les ports configurés dans Docker Compose.

En production, l'accès public passe par Nginx et le nom de domaine configuré. Les URL et ports réels doivent être vérifiés dans la configuration de déploiement.

## Tests

Les tests backend sont exécutés avec `pytest`.

Installer les dépendances dans l'environnement Python approprié :

```bash
pip install -r requirements.txt
```

Exécuter les tests :

```bash
pytest
```

Pour obtenir un rapport de couverture, si `pytest-cov` est installé :

```bash
pytest --cov=app --cov-report=term-missing
```

Les tests doivent notamment couvrir les règles métier, les cas d'utilisation, les validateurs, les dépôts et les interactions avec l'API.

L'objectif de couverture unitaire défini pour le projet est de **80 %**. Ce seuil doit être vérifié à partir du rapport de couverture de la version testée.

## Déploiement en production

Le déploiement en production nécessite une configuration distincte de l'environnement local :

- Définir les variables d'environnement et les secrets sur le serveur.
- Configurer les clés Stripe et le webhook de production.
- Configurer Brevo et une adresse d'expéditeur vérifiée.
- Configurer le domaine, Nginx et HTTPS.
- Vérifier les endpoints MinIO accessibles depuis les conteneurs et, si nécessaire, depuis le navigateur.

Ne copiez pas les secrets de production dans le README ou dans le dépôt Git. Les commandes de déploiement exactes dépendent du fichier Compose de production et de la configuration du serveur.

---

## Dépôts

- **Backend** : [Leila-33/backendmmotors](https://github.com/Leila-33/backendmmotors)
- **Frontend** : [Leila-33/frontend](https://github.com/Leila-33/frontend)
