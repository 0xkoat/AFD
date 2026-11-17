"""Livrable 1 - Dessin de l'automate avec Graphviz."""

import graphviz


def dessiner(afd):
    """Retourne un graphe Graphviz représentant l'automate."""
    graphe = graphviz.Digraph(format="png")
    graphe.attr(rankdir="LR", size="7,5")  # de gauche à droite, image limitée en taille

    # Les états : un double cercle pour les états finaux.
    for etat in sorted(afd.etats):
        if etat in afd.etats_finaux:
            graphe.node(etat, shape="doublecircle")
        else:
            graphe.node(etat, shape="circle")

    # Une flèche qui vient de nulle part désigne l'état initial.
    graphe.node("__debut__", shape="point")
    graphe.edge("__debut__", afd.etat_initial)

    # Les transitions : si plusieurs symboles vont du même état au même état,
    # on dessine une seule flèche avec l'étiquette « a, b ».
    symboles_par_fleche = {}
    for etat in sorted(afd.etats):
        for symbole in sorted(afd.alphabet):
            destination = afd.transitions[etat][symbole]
            fleche = (etat, destination)
            if fleche not in symboles_par_fleche:
                symboles_par_fleche[fleche] = []
            symboles_par_fleche[fleche].append(symbole)

    for (source, destination), symboles in symboles_par_fleche.items():
        graphe.edge(source, destination, label=", ".join(symboles))

    return graphe
