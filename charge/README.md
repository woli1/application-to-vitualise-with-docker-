# Campagnes JMeter

Ce dossier contient les livrables des étapes 15 à 18 :

- `plan.jmx` : connexion puis consultation des notes, avec assertions ;
- `comptes.csv` : 20 comptes de charge ;
- `seed_load_accounts.py` : création des comptes dans la base ;
- `etalonnage.md` : paliers, durée, répétabilité et commandes ;
- `rapport.md` : tableau de synthèse et analyse à compléter avec les mesures.

## Préparer les données

```bash
docker compose up --build -d
docker compose exec backend python -m métier.app.seed
docker compose exec backend python /charge/seed_load_accounts.py
```

## Exécuter une campagne

Installer Apache JMeter 5.6 ou plus récent, puis depuis ce dossier :

```bash
mkdir -p resultats
jmeter -n -t plan.jmx -l resultats/conteneurs-50.jtl \
  -Jhost=localhost -Jport=80 -Jusers=50 -Jramp_up=30 -Jduration=90 \
  -Jaccounts="$PWD/comptes.csv"
```

Les mêmes paliers, le même fichier de comptes, le même scénario et le même
injecteur doivent être utilisés pour les deux déploiements.
