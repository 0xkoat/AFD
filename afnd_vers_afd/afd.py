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
        """Retourne True si le mot est accepté (False sinon, y compris si un symbole est invalide)."""
        etat = self.etat_initial
        for symbole in mot:
            if symbole not in self.alphabet:
                return False
            etat = self.transitions[etat][symbole]
        return etat in self.etats_finaux
