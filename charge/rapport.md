# Rapport de mesure

Ce support doit être complété avec les fichiers `.jtl` et les relevés serveur
pris pendant chaque palier.

| Grandeur | Trois machines virtuelles | Trois conteneurs |
|---|---:|---:|
| Débit maximal soutenu (req/s) | À mesurer | À mesurer |
| Charge au point de saturation (utilisateurs) | À mesurer | À mesurer |
| Latence p95 à charge égale (ms) | À mesurer | À mesurer |
| Taux d'erreur à charge égale | À mesurer | À mesurer |
| Goulet d'étranglement identifié | À expliquer | À expliquer |
| Temps de démarrage complet (s) | À relever | À relever |
| Mémoire consommée au repos (Mo) | À relever | À relever |

L'analyse doit quantifier l'écart de débit, de p95 et de taux d'erreur, puis le
relier aux métriques CPU, mémoire, réseau, connexions et E/S PostgreSQL. Une
moyenne seule ne suffit pas : conserver médiane, p90, p95 et p99.
