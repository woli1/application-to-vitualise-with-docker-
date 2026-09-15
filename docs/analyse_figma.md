# Documentation du Projet - Analyse & Conception Figma

## 1. Introduction et Objectif
Ce projet consiste à développer une application web en architecture **trois-tiers** pour la gestion et la consultation de notes universitaires. L'application gère trois rôles distincts (**Étudiant**, **Enseignant**, et **Superviseur**) avec un système d'authentification par session sécurisée (cookies HttpOnly/CORS) et des mots de passe hachés (`bcrypt`).

---

## 2. Analyse des Besoins et Cas Limites
L'application a été conçue pour répondre à plusieurs cas nominaux et cas limites exigés par le cahier des charges :

* **Côté Étudiant :** 
  * Consultation de ses notes par matière avec affichage du code et de l'intitulé du cours.
* **Côté Enseignant :** 
  * Consultation de la liste des cours qui lui sont assignés (*Cas limite géré : un enseignant sans cours ou avec des cours spécifiques*).
  * Gestion et visualisation des notes des étudiants inscrits à ses cours par ordre décroissant.
* **Côté Superviseur :** 
  * Tableau de bord d'administration permettant de valider ou de refuser les comptes en attente d'inscription (*statut `en_attente`*).

---

## 3. Conception et Maquettage (Figma)
Le design de l'application a été entièrement prototypé sur **Figma** avant le développement.

* **Lien du prototype Figma :** [Accéder au projet Figma](https://www.figma.com/design/9jIbWnN6KMPTkouNwWgmX6/notes?node-id=5-500&t=mnd9WyDwAVQkOf5U-1)

### Principes d'ergonomie et structure des écrans :
* **Écran de Connexion (`index.html`) :**
  * Formulaire centralisé avec gestion des états (bouton "Connexion en cours...", affichage dynamique des erreurs en cas d'identifiants invalides ou de compte en attente).
  * Redirection automatique et intelligente vers le tableau de bord correspondant au rôle récupéré (`cours.html` pour l'enseignant, `validation.html` pour le superviseur, `notes.html` pour l'étudiant).
* **Espace Enseignant (`cours.html` & `notes.html`) :**
  * Une première vue en cartes listant les cours assignés au professeur connecté.
  * Une vue détaillée par cours affichant un tableau récapitulatif des notes des étudiants, avec un bouton de retour rapide et une interface prête pour l'ajout/modification de notes.
* **Espace Superviseur (`validation.html`) :**
  * Un tableau de bord sous forme de liste avec des badges de rôle distincts (bleu pour les étudiants, gris pour les enseignants).
  * Des actions directes de validation (passage du statut à `actif`) ou de refus (suppression de la demande en attente).

---

## 4. Comment reconstruire / déployer le prototype à partir des sources
Si vous souhaitez réinstancier l'application à partir des livrables :

1. **Base de données (Couche Données - `donnees/`) :**
   * Créez une base PostgreSQL nommée `notes`.
   * Exécutez le script de structure `schema.sql` (ou `creation.sql`).
   * Exécutez le script d'insertion `peuplement.sql` pour charger les données de test et les comptes par défaut.
2. **API Backend (Couche Métier - `metier/`) :**
   * Placez-vous dans le dossier `metier/` et installez les dépendances : 
     `pip install -r requirements.txt`
   * Lancez le serveur Flask : `python app.py` (il s'exécute par défaut sur `http://127.0.0.1:5000`).
3. **Interface Frontend (Couche Présentation - `client/`) :**
   * Ouvrez les fichiers HTML via un serveur local (Live Server sur VS Code par exemple) sur le port 8000 (`http://127.0.0.1:8000`).
   * Assurez-vous que l'URL de base dans `app.js` pointe bien vers l'API (`http://127.0.0.1:5000`).