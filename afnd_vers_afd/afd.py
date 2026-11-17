"""Automate fini déterministe (AFD).

Un AFD est un quintuple (Q, A, q0, F, delta) où delta donne UN SEUL état :

    transitions[etat][symbole] = etat_suivant
"""


class AFD:
    def __init__(self, etats, alphabet, etat_initial, etats_finaux, transitions):
        self.etats = etats
        self.alphabet = alphabet
        self.etat_initial = etat_initial
        self.etats_finaux = etats_finaux
        self.transitions = transitions
        self.verifier()

    def verifier(self):
        """Vérifie que l'automate est un AFD complet. Lève ValueError sinon."""
        if self.etat_initial not in self.etats:
            raise ValueError("L'état initial n'est pas dans l'ensemble des états.")

        for etat in self.etats_finaux:
            if etat not in self.etats:
                raise ValueError(f"L'état final « {etat} » n'est pas dans l'ensemble des états.")

        for etat in self.etats:
            for symbole in self.alphabet:
                if symbole not in self.transitions.get(etat, {}):
                    raise ValueError(f"Transition manquante : delta({etat}, {symbole}) n'est pas définie.")

    def reconnaitre(self, mot):
        """Lit le mot caractère par caractère.

        Retourne un triplet (accepte, chemin, symboles_invalides) :
            accepte  : True si le mot est accepté, False sinon
            chemin   : la liste des états parcourus, en partant de l'état initial
            symboles_invalides : les symboles du mot qui ne sont pas dans l'alphabet
        """
        # 1. Signaler les symboles qui n'appartiennent pas à l'alphabet.
        symboles_invalides = sorted({symbole for symbole in mot if symbole not in self.alphabet})
        if len(symboles_invalides) > 0:
            return False, [], symboles_invalides

        # 2. Parcourir les caractères dans l'ordre en appliquant les transitions.
        etat = self.etat_initial
        chemin = [etat]
        for symbole in mot:
            etat = self.transitions[etat][symbole]
            chemin.append(etat)

        # 3. Le mot est accepté si l'état atteint à la fin est un état final.
        accepte = etat in self.etats_finaux
        return accepte, chemin, []


def formater_chemin(mot, chemin):
    """Écrit le chemin parcouru, une transition par ligne : 'A --a--> B'."""
    if mot == "":
        return f"{chemin[0]}  (mot vide : aucune transition)"

    lignes = []
    for i, symbole in enumerate(mot):
        lignes.append(f"{chemin[i]} --{symbole}--> {chemin[i + 1]}")
    return "\n".join(lignes)
