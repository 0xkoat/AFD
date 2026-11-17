# Projet : Théorie des langages et des automates (AFD)

## Installation

1. Installer le logiciel Graphviz (il fournit la commande `dot`) :
   - Linux : `sudo apt install graphviz`
   - Windows : https://graphviz.org/download/ (cocher « ajouter au PATH »)
2. Installer la bibliothèque Python : `pip install graphviz`
3. Tkinter (l'interface) est fourni avec Python (Linux : `sudo apt install python3-tk`).

## Livrable 1 : définition de l'AFD, fonction de transition, interface et visualisation

Dossier `livrable1/`

| Fichier            | Rôle                                                              |
|--------------------|-------------------------------------------------------------------|
| `afd.py`           | La classe `AFD` (Q, A, q0, F, delta) et la lecture des saisies    |
| `visualisation.py` | Le dessin de l'automate avec Graphviz                             |
| `exemple.py`       | Un AFD défini en Python avec un dictionnaire de transitions       |
| `interface.py`     | L'interface : saisie de l'automate + dessin                       |

    cd livrable1
    python exemple.py      # affiche l'automate et crée afd_exemple.png
    python interface.py    # lance l'interface

## Livrable 2 : reconnaissance de mots, tests, interface de test

Dossier `livrable2/` (contient les fichiers du livrable 1, plus :)

| Fichier        | Rôle                                                                  |
|----------------|-----------------------------------------------------------------------|
| `afd.py`       | + la méthode `reconnaitre(mot)` qui retourne (accepté, chemin, symboles invalides) |
| `tests_afd.py` | Tests : mots acceptés, rejetés, mot vide, symboles invalides          |
| `interface.py` | + la zone « Tester un mot » qui affiche le résultat et le chemin parcouru |

    cd livrable2
    python tests_afd.py    # lance les tests
    python interface.py    # lance l'interface

## Format de saisie dans l'interface

- États, alphabet, états finaux : séparés par des virgules (`q0, q1, q2`).
- Transitions : une par ligne, sous la forme `état symbole destination` (`q0 a q1`).
- L'automate doit être **complet** : une transition pour chaque état et chaque symbole.
# AFD
