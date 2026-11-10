# Étalonnage du protocole

## Objectif

Vérifier que l'injecteur JMeter n'est pas le facteur limitant avant de comparer
le déploiement sur trois machines virtuelles avec le déploiement en conteneurs.

## Préparation

```bash
docker compose up --build -d
docker compose exec backend python /charge/seed_load_accounts.py
curl -fsS http://localhost/api/health
```

Le service mesuré doit être seul en fonctionnement. L'injecteur est la machine
hôte, hors des conteneurs.

## Paliers et répétabilité

Les paliers proposés sont `1, 5, 10, 25, 50, 100` utilisateurs. Chaque palier
dure 90 secondes avec 30 secondes de montée. La fenêtre de mesure exclut la
montée. Exécuter deux fois le palier de référence (50 utilisateurs) et accepter
la série seulement si débit et p95 restent à moins de 10 % d'écart.

```bash
mkdir -p resultats
jmeter -n -t plan.jmx -l resultats/conteneurs-50.jtl \
  -Jhost=localhost -Jport=80 -Jusers=50 -Jramp_up=30 -Jduration=90 \
  -Jaccounts="$PWD/comptes.csv"
```

Répéter exactement la même commande pour chaque palier et pour chaque
déploiement. Ne jamais démarrer les deux déploiements en même temps.
