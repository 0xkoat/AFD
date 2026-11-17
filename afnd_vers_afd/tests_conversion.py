"""Tests de la conversion AFND -> AFD.

Test 1 : on compare avec la réponse donnée dans le cours (Fig. 4).
Test 2 : sur 300 AFND aléatoires, l'AFD doit accepter exactement les mêmes mots que l'AFND.

Lancer :  python tests_conversion.py
"""

import random
from itertools import product

from afnd import AFND, EPSILON
from conversion import construire_afd
from exemple import afnd_cours


def afnd_accepte(afnd, mot):
    """Simulation directe de l'AFND (sans utiliser conversion.py) : on explore tous les chemins.

    On part de (état initial, position 0) et on avance soit avec une ε-transition,
    soit en lisant le caractère suivant. Le mot est accepté si on arrive sur un état
    final après avoir lu tout le mot.
    """
    a_visiter = [(afnd.etat_initial, 0)]
    deja_vus = set()

    while len(a_visiter) > 0:
        etat, position = a_visiter.pop()
        if (etat, position) in deja_vus:
            continue
        deja_vus.add((etat, position))

        if position == len(mot) and etat in afnd.etats_finaux:
            return True

        for suivant in afnd.destinations(etat, EPSILON):
            a_visiter.append((suivant, position))
        if position < len(mot):
            for suivant in afnd.destinations(etat, mot[position]):
                a_visiter.append((suivant, position + 1))

    return False


def afnd_aleatoire(hasard):
    """Fabrique un AFND au hasard (3 à 6 états, alphabet {a, b}, avec des ε-transitions)."""
    nombre = hasard.randint(3, 6)
    etats = {str(i) for i in range(nombre)}
    transitions = {}

    for _ in range(hasard.randint(3, 14)):
        etat = str(hasard.randrange(nombre))
        symbole = hasard.choice(["a", "b", EPSILON])
        destination = str(hasard.randrange(nombre))
        if etat not in transitions:
            transitions[etat] = {}
        if symbole not in transitions[etat]:
            transitions[etat][symbole] = set()
        transitions[etat][symbole].add(destination)

    finaux = {etat for etat in etats if hasard.random() < 0.4}
    return AFND(etats, {"a", "b"}, "0", finaux, transitions)


def test_cours():
    """La réponse du cours : 5 états A à E, E est final."""
    afd, noms, etapes = construire_afd(afnd_cours)

    attendu_noms = {
        frozenset({"0", "1", "2", "4", "7"}): "A",
        frozenset({"1", "2", "3", "4", "6", "7", "8"}): "B",
        frozenset({"1", "2", "4", "5", "6", "7"}): "C",
        frozenset({"1", "2", "4", "5", "6", "7", "9"}): "D",
        frozenset({"1", "2", "4", "5", "6", "7", "10"}): "E",
    }
    attendu_transitions = {
        "A": {"a": "B", "b": "C"},
        "B": {"a": "B", "b": "D"},
        "C": {"a": "B", "b": "C"},
        "D": {"a": "B", "b": "E"},
        "E": {"a": "B", "b": "C"},
    }

    ok = True
    ok = ok and noms == attendu_noms
    ok = ok and afd.transitions == attendu_transitions
    ok = ok and afd.etat_initial == "A"
    ok = ok and afd.etats_finaux == {"E"}

    if ok:
        print("OK     test 1 : l'AFD obtenu est exactement celui du cours (A à E, E final)")
    else:
        print("ECHEC  test 1 : l'AFD obtenu est différent de celui du cours")
    return ok


def test_aleatoire():
    hasard = random.Random(2024)    # graine fixe : les tests donnent toujours le même résultat
    mots = []
    for longueur in range(0, 7):
        for lettres in product("ab", repeat=longueur):
            mots.append("".join(lettres))

    erreurs = 0
    for _ in range(300):
        afnd = afnd_aleatoire(hasard)
        afd, noms, etapes = construire_afd(afnd)     # lève une erreur si l'AFD n'est pas complet
        for mot in mots:
            if afd.reconnaitre(mot) != afnd_accepte(afnd, mot):
                erreurs += 1

    if erreurs == 0:
        print(f"OK     test 2 : 300 AFND aléatoires x {len(mots)} mots, l'AFD et l'AFND donnent toujours le même résultat")
    else:
        print(f"ECHEC  test 2 : {erreurs} mots reconnus différemment")
    return erreurs == 0


if __name__ == "__main__":
    resultats = [test_cours(), test_aleatoire()]
    if not all(resultats):
        raise SystemExit(1)
    print("Tous les tests sont réussis.")
