# Guide d'utilisation : DATAS PRE-PROCESSING TOOL

Ce guide explique comment utiliser le **DATAS PRE-PROCESSING TOOL**, notre outil Python basé sur Tkinter et Pandas permettant de visualiser, filtrer et produire un dataset personnalisé à partir d'un JSON.

---

## **1. Installation et préparation**

Avant de lancer le script, assurez-vous d'avoir installé les bibliothèques nécessaires :

```bash
pip install pandas
```

Le JSON doit également être aplati avant usage par pandas. Il est nécessaire d'exécuter une fois le script flatten_datas.py afin de convertir les données.

```bash
python3 flatten_datas.py
```

Pour lancer le programme de pre-traitement

```bash
python3 preprocessing.py
```

## **2. Fonctionnement de l'outil**

L'interface Tkinter est divisée en plusieurs parties :
- **à gauche :** Onglet de gestion des attributs
- **au milieu :** Nettoyage des données
- **à droite :** Filtrage des données (en cours de développement)
- **en bas :** Génération du dataset, export et visualisation des données

### **2.1. Gestion des attributs**

Le script récupère automatiquement toutes les caractéristiques des paquets (clés dictionnaire) et les affiche afin que l'utilisateur puisse choisir lesquelles il souhaite garder dans son dataset personnalisé. Chaque attribut peut être ajouté ou retiré par clic sur le bouton.

### **2.2. Nettoyage des données**

**Gestion des valeurs non définies**

L'activation de cette option entraîne la suppression de toutes les entrées qui ont au moins un attribut indéfini.

**Gestion des valeurs abberantes**

L'activation de cette option permet le réglage d'un seuil. Toutes les entrées étant plus éloignées que le seuil par rapport à la moyenne sont supprimées.

*Note : Il est possible de visualiser combien et sur quels attributs les données ont été supprimées en activant le mode verbose.*

### **2.3. Filtrage des données**

WIP

### **2.4. Génération et export**

Le bouton de gauche permet de générer le dataset personnalisé respectant toutes les conditions fixées précédemment. 

Le bouton du milieu permet de visualiser le dataset complet et celui de droite le dataset personnalisé.

Un export est automatiquement effectué en JSON au moment de la génération du dataset.