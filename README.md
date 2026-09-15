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
uvicorn métier.app.main:app --reload
```

Ouvrir <http://localhost:8000>.

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
