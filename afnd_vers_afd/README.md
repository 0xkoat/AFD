# Conversion d'un AFND en AFD (sans minimisation)

On donne un AFND (avec ou sans ε-transitions), le programme donne l'AFD équivalent
avec l'algorithme **Construction_des_Sous-Ensembles** du cours (chapitre 3).

## Installation

1. Installer Graphviz (il fournit la commande `dot`) :
   - Linux : `sudo apt install graphviz`
   - Windows : https://graphviz.org/download/ (cocher « ajouter au PATH »)
2. Installer la bibliothèque Python : `pip install -r requirements.txt`
3. Tkinter (l'interface) est fourni avec Python (Linux : `sudo apt install python3-tk`).

## Lancer

    python interface.py          # l'interface
    python exemple.py            # l'exemple du cours en console
    python -m unittest           # les 359 tests (ajouter -v pour voir chaque test)

## Les fichiers

| Fichier               | Rôle                                                                        |
|-----------------------|-----------------------------------------------------------------------------|
| `afnd.py`             | La classe `AFND` (delta donne un ensemble d'états, ε autorisé) + lecture des saisies |
| `conversion.py`       | `epsilon_fermeture`, `transiter` et `construire_afd` (l'algorithme du cours) |
| `afd.py`              | La classe `AFD` (le résultat) et `reconnaitre(mot)` : accepté ou non + chemin |
| `visualisation.py`    | Dessin de l'AFND et de l'AFD avec Graphviz                                  |
| `exemple.py`          | L'exemple du cours : (a\|b)*abb, Fig. 2 -> Fig. 4, puis test de mots        |
| `test_afnd.py`        | Tests de `afnd.py` : lecture des saisies, vérifications (138 tests avec `test_afd.py`) |
| `test_afd.py`         | Tests de `afd.py` : reconnaissance de mots, chemin, symboles invalides      |
| `test_conversion.py`  | Tests de `conversion.py` : exemple du cours, cas particuliers, AFND aléatoires |
| `test_visualisation.py` | Tests du dessin (texte Graphviz et image PNG)                             |
| `test_interface.py`   | Tests de l'interface (fenêtre cachée ; ignorés s'il n'y a pas d'écran)     |
| `interface.py`        | Saisie de l'AFND, affichage de l'AFD, de la table, des étapes, et test de mots |
| `captures/`           | Captures d'écran de l'interface                                             |

## Les tests

    python -m unittest                      # tous les tests
    python -m unittest test_conversion -v   # un seul fichier, en détail

Les tests utilisent `unittest` (fourni avec Python, rien à installer). Ils vérifient notamment :
- chaque fonction du cours (`epsilon_fermeture`, `transiter`) sur l'exemple du cours ;
- l'AFD obtenu pour l'exemple du cours (A à E, E final) ;
- des cas particuliers : état puits ∅, ε-cycles, mot vide, AFND sans transition, sans état final...
- le cas où le nombre d'états explose (jusqu'à 2^5 = 32 états) ;
- des centaines d'AFND tirés au hasard : l'AFD accepte exactement les mêmes mots que l'AFND
  (la simulation de l'AFND est écrite à part, sans réutiliser l'algorithme testé) ;
- les messages d'erreur, le dessin Graphviz et l'interface.

## Format de saisie

- États, alphabet, états finaux : séparés par des virgules (`0, 1, 2`).
- Transitions : une par ligne, `état symbole destination` (`0 a 1`).
- ε-transition : `0 ε 1` (ou `0 eps 1`).
- Plusieurs lignes avec le même état et le même symbole = non-déterminisme.

## Tester un mot avec l'AFD

Après la conversion, la zone « Tester un mot avec l'AFD obtenu » (en bas de la fenêtre) permet
de saisir un mot (touche Entrée ou bouton) :

- le mot est **accepté** si l'état atteint à la fin de la lecture est final, sinon il est **rejeté** ;
- le chemin parcouru est affiché (`A --a--> B`) ;
- un symbole qui n'est pas dans l'alphabet est signalé ;
- le mot vide se teste en laissant le champ vide.

## Résultat

- Chaque état de l'AFD est un ensemble d'états de l'AFND (nommé A, B, C...).
- Un état de l'AFD est final s'il contient un état final de l'AFND.
- Si un symbole mène à l'ensemble vide, il devient un état « puits » (noté ∅ dans la table).
- L'AFD obtenu est donc toujours complet.
