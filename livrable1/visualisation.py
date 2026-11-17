import graphviz


def dessiner(afd):
    graphe = graphviz.Digraph(format="png")
    graphe.attr(rankdir="LR", size="7,5") 

    for etat in sorted(afd.etats):
        if etat in afd.etats_finaux:
            graphe.node(etat, shape="doublecircle")
        else:
            graphe.node(etat, shape="circle")
    graphe.node("__debut__", shape="point")
    graphe.edge("__debut__", afd.etat_initial)

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
