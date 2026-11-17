"""Dessin des automates avec Graphviz."""

import graphviz


def creer_graphe(etats, etat_initial, etats_finaux, fleches, libelles):
    """Construit le graphe.

    fleches  : dictionnaire (source, destination) -> liste des symboles de la flèche
    libelles : dictionnaire état -> texte écrit dans le cercle
    """
    graphe = graphviz.Digraph(format="png")
    graphe.attr(rankdir="LR", size="6,4")

    for etat in sorted(etats):
        if etat in etats_finaux:
            graphe.node(etat, label=libelles[etat], shape="ellipse", peripheries="2")  # double contour
        else:
            graphe.node(etat, label=libelles[etat], shape="ellipse")

    # Une flèche qui vient de nulle part désigne l'état initial.
    graphe.node("__debut__", shape="point")
    graphe.edge("__debut__", etat_initial)

    for (source, destination), symboles in fleches.items():
        graphe.edge(source, destination, label=", ".join(symboles))

    return graphe


def ajouter_fleche(fleches, source, destination, symbole):
    """Ajoute un symbole sur la flèche source -> destination (en la créant si besoin)."""
    if (source, destination) not in fleches:
        fleches[(source, destination)] = []
    fleches[(source, destination)].append(symbole)


def dessiner_afnd(afnd):
    fleches = {}
    for etat in sorted(afnd.etats):
        for symbole in sorted(afnd.transitions.get(etat, {})):
            for destination in sorted(afnd.transitions[etat][symbole]):
                ajouter_fleche(fleches, etat, destination, symbole)

    libelles = {etat: etat for etat in afnd.etats}
    return creer_graphe(afnd.etats, afnd.etat_initial, afnd.etats_finaux, fleches, libelles)


def dessiner_afd(afd):
    """Dessine l'AFD (les ensembles d'états de l'AFND sont dans la table de transitions)."""
    fleches = {}
    for etat in sorted(afd.etats):
        for symbole in sorted(afd.alphabet):
            ajouter_fleche(fleches, etat, afd.transitions[etat][symbole], symbole)

    libelles = {etat: etat for etat in afd.etats}
    return creer_graphe(afd.etats, afd.etat_initial, afd.etats_finaux, fleches, libelles)
