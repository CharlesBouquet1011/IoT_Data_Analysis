The plots are in english for a better global understanding of our work but the interface isn't. Please feel free to use Google Traduction integration within the browser to translate from french to english. The Readme is written in French as well for a better time efficiency.

# Lancer le projet
Je conseille d'installer [Docker](https://docs.docker.com/engine/install/) si ce n'est pas déjà fait. Le projet tournera difficilement sans.

Dans le répertoire du projet, faire tout simplement `docker-compose up -d`
Cette commande lancera un nginx, un backend Python et un frontend React.

Pour accéder à l'interface graphique, allez sur http://localhost .

Si React ne fonctionne pas ou pour mettre à jour les librairies utilisées:
`docker-compose exec react sh`
`npm install`
`exit`
# Interface Graphique:

![Interface graphique](ReadmeImgs/interface.png)

# Préparation des données:
Une fois sur l'interface graphique, cliquez sur "Upload", choississez vos données à upload. Ces données doivent être les données d'un mois entier.
Une fois téléchargées, vous pouvez maintenant choisir sur quels paramètres seront appliqués le prétraitement des données pour filtrer les valeurs aberrantes (pour plus d'informations, voir notre rapport technique).

Attendez un peu, et voilà vos données sont prêtes à être exploitées !

# Exploitation des données:
Vous pouvez maintenant choisir entre traitement et Prédiction

# Traitement:
Dans ce menu, vous pouvez choisir entre plusieurs options:
- Régression/prédiction entraîne un modèle d'IA pour dégager une tendance dans les données et pour trouver quelles paramètres physiques impactent le plus une prédiction
- Analyse de la saisonnalité fait des plots à diverses échelles pour voir si le traffic d'un réseau LoRaWan est saisonnier comme dans un réseau classique avec du traffic humain.
- Clustering permet de plot un paramètre physique en fonction d'un ou de deux autres paramètres physiques pour essayer de trouver à vue d'oeil des corrélations.
- Statistiques vous permet de plot diverses statistiques générales du réseau afin de dégager une compréhension globale de l'utilisation du réseau: proportion des paquets qui utilisent un paramètre, répartition par type parmis ces paquets qui utilisent ce paramètre, ...

# Prédiction:
Dans cette partie, on essaie de rassembler les paquets par leur empreinte physique pour éviter le spoofind dans le cadre du Dev_Eui ou pour trouver le nombre de devices dans le réseau dans le cadre du Dev_Add
On peut soit se baser sur le Dev_Eui (peu de données) ou le Dev_Add (beaucoup de données mais ce paramètre change fréquemment au cours des communications).


# Librairies utilisées
- FastAPI (pour les requêtes http backend)
- uvicorn pour l'autoreload et serve le backend
- Pandas  (pour le traitement des données)
- scikit-learn pour les entraînements d'arbres de décisions
- hdbscan pour le clustering dans la section prédiction
- ijson pour lire des jsons lignes par ligne (pour les gros volumes de données)
- pyarrow pour écrire des .parquets
- cachetool pour optimiser quelque peu sur des faibles volumes de données
- Matplotlib pour les plot
- React Js pour l'interface graphique


### Contexte
Titouan Verdier, Paul-Henri Lucotte, David Magoudaya, Charles Bouquet.
Nous devions analyser des données dans le cadre du projet SIR Data Analysis for Internet of Things du département Télécommunications à l'INSA Lyon encadré par Fabrice Valois et Oana Iova. Les données sur lesquelles nous travaillions sont issues de données réelles prélevées sur les deux antennes du campus de la Doua par Fabrice Valois et Oana Iova.

![Logo INSA](https://www.insa-lyon.fr/sites/www.insa-lyon.fr/files/logo-version1.jpg)
![Logo TC](https://media.licdn.com/dms/image/v2/C4D1BAQH1qpNIX74MqQ/company-background_10000/company-background_10000/0/1583771497171/tcinsalyon_cover?e=2147483647&v=beta&t=iPtkU0fWyDY_rm0la5reWqcORwoLDZa8BBaGEDF4Wuc)