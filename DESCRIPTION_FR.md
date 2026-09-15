# ENCYCLOPE

**ENCYCLOPE** est un projet d'encyclopédie locale conçu pour permettre aux utilisateurs de rechercher, collecter, stocker et lire des informations directement sur leur ordinateur.

Le projet utilise **Wikipédia comme principale source d'information**. Les articles peuvent être recherchés en ligne, téléchargés puis enregistrés dans une base de données locale. Une fois qu'un article a été enregistré, il peut être recherché et lu localement sans avoir besoin de le télécharger à nouveau.

## Fonctionnalités principales

ENCYCLOPE comprend plusieurs outils conçus pour permettre de créer facilement sa propre encyclopédie :

* **Recherche d'articles** — Rechercher sur Wikipédia une personne, un lieu, un événement, un sujet scientifique, une technologie, un sujet culturel ou presque n'importe quel autre sujet.
* **Stockage local** — Enregistrer les articles dans une base de données SQLite locale.
* **Lecture hors ligne** — Lire les articles déjà téléchargés sans avoir besoin de les demander à nouveau à Wikipédia.
* **Crawler** — Explorer automatiquement les pages Wikipédia et enregistrer plusieurs articles liés.
* **Crawler multiple** — Rechercher plusieurs sujets en même temps.
* **Recherche locale** — Rechercher des mots ou des phrases parmi tous les articles enregistrés localement.
* **Lecteur d'articles** — Ouvrir et lire les articles enregistrés dans leur intégralité.
* **Thèmes** — Voir les différents sujets utilisés pour collecter les articles.
* **Statistiques** — Consulter le nombre d'articles enregistrés, la taille de la base de données et l'espace disponible.
* **Suppression d'articles** — Supprimer des articles individuellement, des groupes de résultats ou toute la base de données.
* **Base de données locale** — Toutes les informations collectées sont enregistrées avec SQLite.

## Système de Crawler

L'une des principales fonctionnalités d'ENCYCLOPE est son crawler.

Au lieu de télécharger manuellement chaque article, le crawler peut partir d'un sujet et explorer automatiquement les pages Wikipédia qui lui sont liées.

Par exemple, l'utilisateur peut lancer un crawler sur :

`Mars`

Le crawler peut ensuite découvrir des pages liées grâce aux liens présents sur Wikipédia et les enregistrer dans la base de données locale.

Il est également possible de lancer plusieurs sujets, par exemple :

`Mars, Napoléon, Paris, Python`

Cela permet à ENCYCLOPE de construire progressivement une grande base personnelle de connaissances.

## Base de données locale

ENCYCLOPE utilise une base de données SQLite appelée `encyclope.db`.

La base de données enregistre notamment :

* Les titres des articles
* Les URL des articles
* Le texte des articles
* De courts résumés
* Les thèmes
* Les dates de création
* Les liens entre les articles

Le projet actuel est conçu pour pouvoir stocker **jusqu'à 10 000 articles**.

Cette limite représente la capacité maximale configurée pour la version actuelle et non le nombre d'articles déjà présents dans le projet.

## Simple et local

ENCYCLOPE est conçu pour rester simple.

Il ne nécessite pas de système de compte en ligne compliqué. La base de données est enregistrée localement sur l'ordinateur de l'utilisateur, ce qui permet de conserver facilement sa propre collection d'informations.

Le projet est développé en **Python** et utilise **SQLite** pour le stockage local.

## Version bêta

⚠️ **ENCYCLOPE est actuellement en version bêta.**

Le projet est toujours en cours de développement. Certaines fonctionnalités peuvent donc être incomplètes, instables ou contenir des bugs. Certaines situations peuvent également provoquer des erreurs inattendues, notamment lors du téléchargement ou du traitement de certaines pages Wikipédia.

La version actuelle doit donc être considérée comme une **version de développement et de test**, et non comme un produit terminé.

L'objectif est de continuer à améliorer ENCYCLOPE en corrigeant les bugs, en améliorant le crawler, en rendant les recherches plus rapides et fiables, en améliorant la base de données et en ajoutant de nouvelles fonctionnalités.

## Développements futurs

ENCYCLOPE continue d'évoluer. Les futures versions pourraient inclure des améliorations telles que :

* Un crawler plus rapide et plus puissant
* Une meilleure classification des articles
* Une recherche améliorée
* Une meilleure gestion des pages Wikipédia
* Davantage d'outils de gestion de la base de données
* De meilleures performances
* Une interface graphique
* Une organisation plus avancée des connaissances
* De meilleures connexions entre les articles liés

Le projet peut donc évoluer de manière importante au fur et à mesure de son développement.

## Projet Open Source

ENCYCLOPE est un projet personnel expérimental créé pour explorer la programmation, les bases de données, la collecte de données sur le Web et la création d'un système local de connaissances.

Le projet est partagé publiquement afin que d'autres personnes puissent le découvrir, le tester, signaler des bugs et éventuellement proposer des idées ou des améliorations.

## Avis important

ENCYCLOPE récupère des informations depuis **Wikipédia**. Le projet ne crée pas et ne vérifie pas les informations présentes dans les articles d'origine.

L'exactitude, l'exhaustivité et la disponibilité des informations collectées dépendent donc des pages Wikipédia d'origine ainsi que de la capacité du crawler à les traiter correctement.

ENCYCLOPE doit être considéré comme un outil permettant de collecter et d'organiser des informations, et non comme un remplacement de la consultation des sources originales.

---

**ENCYCLOPE — Une encyclopédie locale développée en Python.**

*Version bêta — Projet en cours de développement.*
