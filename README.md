# Notes

Application de gestion des étudiants basée sur le prototype Figma : connexion, notes étudiant, cours enseignant et validation des comptes.

## Stack

- Frontend : HTML, Tailwind CSS via CDN, JavaScript vanilla
- Backend : Python, FastAPI, SQLAlchemy
- Base de données : PostgreSQL 16

## Démarrage avec PostgreSQL installé localement

### 1. Créer la base PostgreSQL

Le nom de la base de données est **`notes_db`**. Ouvre un terminal et connecte-toi avec l'utilisateur administrateur PostgreSQL (`postgres`) :

```bash
sudo -u postgres psql
```

Dans `psql`, exécute :

```sql
CREATE USER notes_user WITH PASSWORD 'notes_password';
CREATE DATABASE notes_db OWNER notes_user;
\q
```

Si l'utilisateur ou la base existe déjà, PostgreSQL affichera une erreur `already exists` : dans ce cas, continue simplement avec l'étape suivante.

Teste ensuite la connexion :

```bash
psql -h localhost -U notes_user -d notes_db
```

Dans `psql`, crée les tables avec le script fourni :

```sql
\i sql/init.sql
\dt
\q
```

Tu peux aussi laisser FastAPI les créer automatiquement au démarrage. Le fichier [sql/init.sql](sql/init.sql) est recommandé si tu veux contrôler la création manuellement.

### 2. Installer Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Ajouter les données de démonstration

```bash
python3 -m métier.app.seed
```

Les comptes de démonstration sont prévus dans le seed :

- étudiant : `abdelhamid.tan@etu.univ-amu.fr`
- enseignant : `m.ksouri@ecole.fr`

Après une inscription, le compte reste en attente jusqu'à sa validation par un superviseur. L'utilisateur peut ensuite se connecter avec l'email et le mot de passe choisis lors de l'inscription.

### 4. Lancer l'application

```bash
uvicorn métier.app.main:app --host 0.0.0.0 --port 8000
```

Ouvrir <http://localhost:8000>.

## Injection de charge avec JMeter

Les livrables de la mesure demandée sont dans le dossier [charge/](charge/).
Le plan reproduit le parcours étudiant en deux requêtes : connexion puis
consultation des notes. Il contient un gestionnaire de cookies, un fichier de
20 comptes, un temps de réflexion et des assertions sur les réponses.

Après le démarrage Docker, préparer les comptes :

```bash
docker compose exec backend python -m métier.app.seed
docker compose exec backend python /charge/seed_load_accounts.py
```

Puis suivre [charge/README.md](charge/README.md) et
[charge/etalonnage.md](charge/etalonnage.md) pour exécuter les paliers
`1, 5, 10, 25, 50, 100` utilisateurs. Les résultats bruts doivent être
conservés dans `charge/resultats/` et reportés dans
[charge/rapport.md](charge/rapport.md).

## Déploiement sur trois machines virtuelles

Les adresses réseau utilisées sont les suivantes :

| VM | Adresse | Rôle |
| --- | --- | --- |
| Frontend | `172.16.0.10` / `9.205.104.14` | Fichiers HTML, CSS, JavaScript et reverse proxy Nginx |
| Backend | `172.16.1.4` | FastAPI sur le port `8000` |
| Base de données | `172.16.2.4` | PostgreSQL sur le port `5432` |

### VM base de données

PostgreSQL doit écouter sur le réseau privé et autoriser l'adresse privée du backend :

- `listen_addresses = '172.16.2.4'` dans `postgresql.conf`
- Une règle dans `pg_hba.conf` autorisant `172.16.1.4/32` pour `notes_db`
- Le pare-feu doit autoriser TCP `5432` depuis `172.16.1.4` uniquement

### VM backend

Copier `.env.example` en `.env`, puis démarrer le backend avec :

```bash
DATABASE_URL=postgresql+psycopg://notes_user:notes_password@172.16.2.4:5432/notes_db
uvicorn métier.app.main:app --host 0.0.0.0 --port 8000
```

Le pare-feu du backend doit autoriser TCP `8000` depuis `172.16.0.10` uniquement.

### VM frontend

Installer Nginx, copier le contenu de `client/` dans `/var/www/notes/client`, puis installer
`deploiement/frontend-nginx.conf` dans `/etc/nginx/sites-available/notes` et l'activer.
Le proxy transmet `/api` vers `http://172.16.1.4:8000`, tandis que les utilisateurs
accèdent au frontend via `http://9.205.104.14`.

Le frontend utilise `/api` par défaut : les appels restent donc sur le même domaine public
et Nginx les relaie vers le backend privé. Pour un autre routage, définir
`window.API_BASE_URL` avant `client/app.js`.

## Ce que tu dois faire dans PostgreSQL

Tu dois créer une seule base : **`notes_db`**. Ensuite, le script SQL crée ces quatre tables :

| Table | Utilité |
| --- | --- |
| `users` | étudiants, enseignants et superviseurs |
| `courses` | cours et enseignant responsable |
| `grades` | note d'un étudiant pour un cours |
| `registration_requests` | demandes d'inscription à valider |

Pour vérifier :

```bash
psql -h localhost -U notes_user -d notes_db
\dt
SELECT * FROM users;
SELECT * FROM courses;
SELECT * FROM grades;
```

Pour supprimer et recréer la base pendant le développement :

```bash
sudo -u postgres dropdb notes_db
sudo -u postgres createdb -O notes_user notes_db
psql -h localhost -U notes_user -d notes_db -f sql/init.sql
```

## API principale

- `GET /api/health`
- `GET /api/students/{student_id}/grades`
- `GET /api/courses`
- `GET /api/courses/{course_id}/grades`
- `POST /api/courses/{course_id}/grades`
- `GET /api/registration-requests`
- `POST /api/registration-requests`
- `PATCH /api/registration-requests/{id}/approve`
- `PATCH /api/registration-requests/{id}/reject`
