# Livrable - Deploiement sur trois machines virtuelles

## 1. Architecture et plan d'adressage

L'application est deployee selon une architecture trois-tiers :

```text
Client web
    |
    v
VM proxy/frontend (Nginx) -----> VM metier/backend (FastAPI) -----> VM donnees (PostgreSQL)
        172.16.0.10                     172.16.1.4:8000                 172.16.2.4:5432
        port 80
```

| Machine virtuelle | Nom logique | Adresse privee | Service | Port |
| --- | --- | --- | --- | --- |
| 1 | `vm-proxy` | `172.16.0.10` | Nginx et fichiers frontend | `80/tcp` |
| 2 | `vm-metier` | `172.16.1.4` | FastAPI/Uvicorn | `8000/tcp` |
| 3 | `vm-donnees` | `172.16.2.4` | PostgreSQL | `5432/tcp` |

L'adresse publique utilisee pour acceder au site est `9.205.104.14`. Le backend et
la base de donnees ne sont pas exposes directement au navigateur : les echanges
passent par les adresses privees.

> Le sujet illustre peut utiliser le reseau `10.10.10.0/24`. Dans ce cas, il faut
> remplacer les trois adresses ci-dessus partout, en conservant le meme principe
> de routage. Les commandes ci-dessous correspondent a la configuration actuelle
> du projet.

## 2. Configuration de `vm-proxy`

Installer Nginx et Git :

```bash
sudo apt update
sudo apt install -y git nginx
```

Recuperer le projet et installer le frontend :

```bash
git clone <URL_DU_DEPOT> ~/application-to-virtualise
cd ~/application-to-virtualise
sudo mkdir -p /var/www/notes/client
sudo cp -r client/* /var/www/notes/client/
```

Installer la configuration du reverse proxy :

```bash
sudo cp deploiement/frontend-nginx.conf /etc/nginx/sites-available/notes
sudo ln -s /etc/nginx/sites-available/notes /etc/nginx/sites-enabled/notes
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
```

Configuration Nginx utilisee :

```nginx
server {
    listen 80;
    server_name 9.205.104.14 172.16.0.10;

    root /var/www/notes/client;
    index index.html;

    location /api/ {
        proxy_pass http://172.16.1.4:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Autoriser HTTP :

```bash
sudo ufw allow 80/tcp
```

## 3. Configuration de `vm-metier`

Installer Python et creer l'environnement virtuel :

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
git clone <URL_DU_DEPOT> ~/application-to-virtualise
cd ~/application-to-virtualise
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Creer `.env` a partir de `.env.example` :

```env
DATABASE_URL=postgresql+psycopg://notes_user:notes_password@172.16.2.4:5432/notes_db
APP_ENV=production
CORS_ORIGINS=http://172.16.0.10,http://9.205.104.14
```

Demarrer FastAPI :

```bash
source venv/bin/activate
uvicorn métier.app.main:app --host 0.0.0.0 --port 8000
```

Le backend doit ecouter sur `0.0.0.0:8000`, et non uniquement sur
`127.0.0.1:8000`, afin que `vm-proxy` puisse le joindre.

Autoriser uniquement la VM proxy :

```bash
sudo ufw allow from 172.16.0.10 to any port 8000 proto tcp
```

## 4. Configuration de `vm-donnees`

PostgreSQL doit ecouter sur son adresse privee `172.16.2.4`.

Dans `postgresql.conf` :

```conf
listen_addresses = '172.16.2.4'
```

Dans `pg_hba.conf`, autoriser uniquement le backend :

```conf
host    notes_db    notes_user    172.16.1.4/32    scram-sha-256
```

Creer l'utilisateur et la base :

```bash
sudo -u postgres psql
```

```sql
CREATE USER notes_user WITH PASSWORD 'notes_password';
CREATE DATABASE notes_db OWNER notes_user;
\q
```

Autoriser uniquement `vm-metier` :

```bash
sudo ufw allow from 172.16.1.4 to any port 5432 proto tcp
sudo systemctl restart postgresql
```

## 5. Verification du deploiement

Sur `vm-metier`, verifier le backend :

```bash
curl http://127.0.0.1:8000/api/health
curl http://172.16.1.4:8000/api/health
```

Resultat attendu :

```json
{"status":"ok"}
```

Sur `vm-proxy`, verifier la communication vers le backend :

```bash
ping -c 2 172.16.1.4
curl http://172.16.1.4:8000/api/health
curl http://localhost/api/health
```

Le dernier appel verifie le reverse proxy Nginx. Il doit egalement retourner :

```json
{"status":"ok"}
```

Depuis un navigateur, ouvrir ensuite :

```text
http://9.205.104.14
```

Commandes de controle a joindre au livrable :

```bash
hostname -I
ip addr
ss -lntp | grep -E ':(80|8000|5432)'
sudo nginx -t
sudo systemctl status nginx --no-pager
```

## 6. Regles de circulation

| Source | Destination | Port | Autorisation |
| --- | --- | --- | --- |
| Utilisateur | `vm-proxy` | `80` | Autorisee |
| `vm-proxy` (`172.16.0.10`) | `vm-metier` (`172.16.1.4`) | `8000` | Autorisee |
| `vm-metier` (`172.16.1.4`) | `vm-donnees` (`172.16.2.4`) | `5432` | Autorisee |
| Utilisateur | `vm-metier` | `8000` | Interdite/non necessaire |
| Utilisateur | `vm-donnees` | `5432` | Interdite |
