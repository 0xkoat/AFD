"""Conversion d'un AFND en AFD : algorithme Construction_des_Sous-Ensembles (cours, chapitre 3).

Chaque état de l'AFD est un ENSEMBLE d'états de l'AFND.
(La minimisation de l'AFD n'est pas faite ici.)
"""

from afd import AFD
from afnd import EPSILON


def trier(etats):
    """Trie des états pour l'affichage : '2' avant '10' (on trie d'abord par longueur du nom)."""
    return sorted(etats, key=lambda etat: (len(etat), etat))


def texte_ensemble(ensemble):
    """{'1', '0'} -> '{0, 1}'   et   ensemble vide -> '∅'"""
    if len(ensemble) == 0:
        return "∅"
    return "{" + ", ".join(trier(ensemble)) + "}"


# ----------------------------------------------------------------------
# Les deux définitions du cours
# ----------------------------------------------------------------------

def epsilon_fermeture(afnd, ensemble):
    """ε-fermeture(T) : états de l'AFND accessibles depuis un état de T par des ε-transitions
    uniquement (les états de T eux-mêmes en font partie)."""
    fermeture = set(ensemble)
    a_traiter = list(ensemble)

    while len(a_traiter) > 0:
        etat = a_traiter.pop()
        for suivant in afnd.destinations(etat, EPSILON):
            if suivant not in fermeture:
                fermeture.add(suivant)
                a_traiter.append(suivant)

    return fermeture


def transiter(afnd, ensemble, symbole):
    """Transiter(T, x) : états de l'AFND atteints depuis un état de T en lisant le symbole x."""
    atteints = set()
    for etat in ensemble:
        atteints = atteints | afnd.destinations(etat, symbole)
    return atteints


# ----------------------------------------------------------------------
# L'algorithme
# ----------------------------------------------------------------------

def nom_etat(numero):
    """Nom de l'état de l'AFD : A, B, C, ... (comme dans le cours), puis S26, S27, ..."""
    if numero < 26:
        return chr(ord("A") + numero)
    return f"S{numero}"


def construire_afd(afnd):
    """Transforme l'AFND en AFD.

    Retourne un triplet (afd, noms, etapes) :
        afd    : l'AFD obtenu
        noms   : dictionnaire  ensemble d'états de l'AFND (frozenset) -> nom de l'état dans l'AFD
        etapes : liste de textes expliquant chaque calcul (comme dans les exemples du cours)
    """
    etapes = []

    # Considérer ε-fermeture(e0) comme l'unique état de D_etats, cet état est non marqué.
    depart = frozenset(epsilon_fermeture(afnd, {afnd.etat_initial}))
    d_etats = [depart]          # D_etats : la liste des états de l'AFD (ce sont des ensembles)
    d_trans = {}                # D_trans[T][x] = U
    etapes.append(f"Départ : ε-fermeture({afnd.etat_initial}) = {texte_ensemble(depart)}")

    # Les états d_etats[0 : marques] sont marqués, les suivants ne le sont pas.
    marques = 0

    # tant qu'il existe un état non marqué T dans D_etats faire
    while marques < len(d_etats):
        T = d_etats[marques]
        marques = marques + 1       # marquer T
        d_trans[T] = {}
        etapes.append("")
        etapes.append(f"Traitement de T = {texte_ensemble(T)}")

        # pour chaque symbole x de l'alphabet faire
        for x in sorted(afnd.alphabet):
            atteints = transiter(afnd, T, x)
            U = frozenset(epsilon_fermeture(afnd, atteints))
            etapes.append(
                f"  Pour {x} : Transiter(T, {x}) = {texte_ensemble(atteints)}"
                f"   U = ε-fermeture(...) = {texte_ensemble(U)}"
            )

            # si U n'appartient pas à D_etats alors ajouter U comme nœud non marqué
            if U not in d_etats:
                d_etats.append(U)

            d_trans[T][x] = U

    # --- On donne un nom à chaque état de l'AFD et on construit l'AFD ---
    noms = {}
    for numero, T in enumerate(d_etats):
        noms[T] = nom_etat(numero)

    # Un état de l'AFD est final s'il contient au moins un état final de l'AFND.
    finaux = set()
    for T in d_etats:
        if len(T & afnd.etats_finaux) > 0:
            finaux.add(noms[T])

    transitions = {}
    for T in d_etats:
        transitions[noms[T]] = {}
        for x in afnd.alphabet:
            transitions[noms[T]][x] = noms[d_trans[T][x]]

    afd = AFD(set(noms.values()), set(afnd.alphabet), noms[depart], finaux, transitions)
    return afd, noms, etapes


# ----------------------------------------------------------------------
# Affichage de la table de transitions de l'AFD
# ----------------------------------------------------------------------

def table_afd(afd, noms):
    """Retourne la table de transitions de l'AFD sous forme de texte."""
    contenu = {}                        # nom -> ensemble d'états de l'AFND
    for ensemble, nom in noms.items():
        contenu[nom] = ensemble

    symboles = sorted(afd.alphabet)
    noms_tries = sorted(afd.etats, key=lambda nom: (len(nom), nom))

    lignes = []
    entete = f"{'':4}{'État':6}{'Ensemble (AFND)':28}" + "".join(f"{x:6}" for x in symboles)
    lignes.append(entete)
    lignes.append("-" * len(entete))

    for nom in noms_tries:
        marque = ""
        if nom == afd.etat_initial:
            marque += "->"
        if nom in afd.etats_finaux:
            marque += "*"
        ligne = f"{marque:4}{nom:6}{texte_ensemble(contenu[nom]):28}"
        ligne += "".join(f"{afd.transitions[nom][x]:6}" for x in symboles)
        lignes.append(ligne)

    lignes.append("")
    lignes.append("->  état initial          *  état final (contient un état final de l'AFND)")
    return "\n".join(lignes)
