# Gestion d'Automates Finis

Un système complet en Python pour la manipulation, l'analyse et la transformation d'automates finis déterministes et non-déterministes.

## 📋 Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure des données](#structure-des-données)
- [Fonctions principales](#fonctions-principales)
- [Exemples](#exemples)

## 📝 Description

Ce projet implémente une bibliothèque complète pour travailler avec des automates finis, incluant :
- La création et la manipulation d'automates déterministes et non-déterministes
- Les opérations classiques sur les automates (complétion, déterminisation, complémentaire)
- Les transformations (élimination des epsilon-transitions, nettoyage)
- Les opérations binaires (concaténation, produit)
- Une interface console interactive pour faciliter l'utilisation
- La sauvegarde et le chargement d'automates depuis des fichiers

## ✨ Fonctionnalités

### Fonctions de base
- ✅ Vérification si un automate est complet
- ✅ Complétion d'automate (ajout d'état puits si nécessaire)
- ✅ Création de l'automate complémentaire
- ✅ Analyse de mots (déterministe et non-déterministe)

### Transformations
- ✅ Déterminisation d'automate non-déterministe
- ✅ Élimination des transitions epsilon
- ✅ Nettoyage (suppression des états inutiles)

### Opérations binaires
- ✅ Concaténation de deux automates
- ✅ Produit de deux automates (intersection des langages)

### Interface utilisateur
- ✅ Menu interactif en console
- ✅ Création d'automate via interface
- ✅ Sauvegarde et chargement depuis fichiers
- ✅ Affichage formaté des automates

## 🔧 Installation

Aucune dépendance externe n'est requise. Le code utilise uniquement la bibliothèque standard de Python 3.

```bash
# Assurez-vous d'avoir Python 3 installé
python3 --version

# Clonez ou téléchargez le fichier vacances.py
```

## 🚀 Utilisation

### Lancement de l'interface interactive

```bash
python3 vacances.py
```

Cela lance un menu interactif avec les options suivantes :

1. **Gérer les automates** : Créer, charger, lister et sélectionner des automates
2. **Opérations sur les automates** : Effectuer diverses opérations sur l'automate courant

### Utilisation programmatique

```python
from vacances import *

# Créer un automate simple
automate = {
    "matrice": [[1, -1], [-1, 1]],
    "finaux": [1],
    "Initial": 0,
    "alphabet": ["a", "b"]
}

# Analyser un mot
mot = [0, 1]  # Indices correspondant à "a", "b"
resultat = Analyse_mot(automate, mot)
print(f"Le mot est accepté : {resultat}")

# Déterminiser un automate
automate_det = Determinister(automate)

# Sauvegarder dans un fichier
save_automates("mes_automates.txt", {"mon_automate": automate})

# Charger depuis un fichier
automates = load_automates("mes_automates.txt")
```

## 📊 Structure des données

Un automate est représenté par un dictionnaire Python avec les clés suivantes :

```python
automate = {
    "matrice": [
        [1, -1],    # État 0 : transition avec symbole 0 -> état 1, symbole 1 -> aucune
        [-1, 1]     # État 1 : transition avec symbole 0 -> aucune, symbole 1 -> état 1
    ],
    "finaux": [1],           # Liste des états finaux
    "Initial": 0,            # État initial (peut aussi être "initial")
    "alphabet": ["a", "b"]   # Liste des symboles (optionnel)
}
```

### Format de la matrice
- **Entier** : Transition déterministe vers l'état correspondant
- **Liste** : Transition non-déterministe vers plusieurs états
- **-1** : Aucune transition

### Exemple d'automate non-déterministe
```python
automate_nd = {
    "matrice": [
        [[1, 2], -1],  # État 0 : symbole 0 peut aller vers état 1 OU 2
        [-1, [0, 1]]   # État 1 : symbole 1 peut aller vers état 0 OU 1
    ],
    "finaux": [1],
    "Initial": 0,
    "alphabet": ["a", "b"]
}
```

## 🔍 Fonctions principales

### `Analyse_mot(automate, mot, verbose=False)`
Analyse si un mot est accepté par l'automate.
- **Paramètres** :
  - `automate` : Dictionnaire représentant l'automate
  - `mot` : Liste d'indices de symboles
  - `verbose` : Afficher les détails du parcours
- **Retourne** : `True` si le mot est accepté, `False` sinon

### `Complet(automate)`
Complète un automate en ajoutant un état puits si nécessaire.
- **Retourne** : Une copie de l'automate complété

### `Complementaire(automate)`
Crée l'automate complémentaire (accepte les mots refusés par l'original).
- **Retourne** : L'automate complémentaire

### `Determinister(automate)`
Convertit un automate non-déterministe en automate déterministe.
- **Retourne** : L'automate déterminisé

### `eliminer_transitions_epsilon(automate, epsilon="EPS")`
Supprime les transitions epsilon d'un automate.
- **Paramètres** :
  - `automate` : L'automate source
  - `epsilon` : Le symbole epsilon utilisé
- **Retourne** : L'automate sans epsilon-transitions

### `concatener(automate1, automate2)`
Concatène deux automates (langage = L1 · L2).
- **Retourne** : L'automate résultant de la concaténation

### `produit(A1, A2)`
Calcule le produit de deux automates (intersection des langages).
- **Retourne** : L'automate produit, ou `0` si les alphabets n'ont pas de caractères communs

### `nettoyer(automate)`
Supprime les états inutiles (inaccessibles ou non co-accessibles).
- **Retourne** : L'automate nettoyé

### `save_automates(fichier, automates_dict, fusionner=False)`
Sauvegarde des automates dans un fichier.
- **Paramètres** :
  - `fichier` : Chemin du fichier
  - `automates_dict` : Dictionnaire nom -> automate
  - `fusionner` : Fusionner avec les automates existants

### `load_automates(fichier)`
Charge des automates depuis un fichier.
- **Retourne** : Dictionnaire nom -> automate

## 📝 Format de fichier

Les automates sont sauvegardés dans un format texte simple :

```
nom|matrice|finaux|initial|alphabet;
```

Exemple :
```
automate_exemple|[[1, -1], [-1, 1]]|[1]|0|['a', 'b'];
```

## 💡 Exemples

### Exemple 1 : Automate acceptant les mots se terminant par "ab"

```python
automate = {
    "matrice": [
        [1, 0],  # État 0
        [-1, 2], # État 1
        [1, 0]   # État 2
    ],
    "finaux": [2],
    "Initial": 0,
    "alphabet": ["a", "b"]
}

# Test
mot1 = [0, 1]  # "ab" -> accepté
mot2 = [0, 1, 0, 1]  # "abab" -> accepté
mot3 = [1, 0]  # "ba" -> refusé

print(Analyse_mot(automate, mot1))  # True
print(Analyse_mot(automate, mot2))  # True
print(Analyse_mot(automate, mot3))  # False
```

### Exemple 2 : Déterminisation

```python
# Automate non-déterministe
automate_nd = {
    "matrice": [
        [[0, 1], -1],
        [-1, [1, 2]],
        [-1, -1]
    ],
    "finaux": [2],
    "Initial": 0,
    "alphabet": ["a", "b"]
}

# Déterminiser
automate_det = Determinister(automate_nd)
afficher_automate(automate_det, "Automate déterminisé")
```

### Exemple 3 : Concaténation

```python
auto1 = {
    "matrice": [[1], [-1]],
    "finaux": [1],
    "Initial": 0,
    "alphabet": ["a"]
}

auto2 = {
    "matrice": [[1], [-1]],
    "finaux": [1],
    "Initial": 0,
    "alphabet": ["b"]
}

auto_concat = concatener(auto1, auto2)
# Accepte les mots de la forme "a" suivi de "b"
```

## 🎯 Cas d'usage

Ce projet est utile pour :
- L'apprentissage de la théorie des automates
- Les exercices et travaux pratiques sur les automates finis
- Les prototypes d'algorithmes sur les langages formels
- Les outils pédagogiques pour l'enseignement

## ⚠️ Notes importantes

- Les indices des états commencent à 0
- Les indices des symboles correspondent à l'ordre dans l'alphabet
- Les transitions manquantes sont représentées par `-1`
- L'interface console utilise `eval()` pour parser les fichiers - assurez-vous que les fichiers sont de confiance
- Pour les automates avec epsilon, le symbole peut être `"$"`, `"EPS"`, `"ε"`, `"epsilon"` ou `"eps"`

## 📄 Licence

Ce code est fourni tel quel, sans garantie. Libre d'utilisation pour l'apprentissage et l'enseignement.

## 👤 Auteur

Développé pour la gestion et l'analyse d'automates finis en Python.