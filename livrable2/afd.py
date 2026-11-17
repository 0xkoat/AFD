"""Livrables 1 et 2 - Définition d'un automate fini déterministe (AFD) et reconnaissance de mots.

Un AFD est un quintuple (Q, A, q0, F, delta) :
    Q  : l'ensemble des états
    A  : l'alphabet
    q0 : l'état initial
    F  : l'ensemble des états finaux
    delta : la fonction de transition, représentée par un dictionnaire Python
            transitions[etat][symbole] = etat_suivant
"""


class AFD:
    def __init__(self, etats, alphabet, etat_initial, etats_finaux, transitions):
        self.etats = etats                  # ensemble de textes, ex : {'q0', 'q1'}
        self.alphabet = alphabet            # ensemble de caractères, ex : {'a', 'b'}
        self.etat_initial = etat_initial    # un texte, ex : 'q0'
        self.etats_finaux = etats_finaux    # ensemble de textes, ex : {'q1'}
        self.transitions = transitions      # dictionnaire de dictionnaires
        self.verifier()

    def verifier(self):
        """Vérifie que l'automate est correct. Lève ValueError sinon."""
        if len(self.etats) == 0:
            raise ValueError("L'ensemble des états est vide.")

        if len(self.alphabet) == 0:
            raise ValueError("L'alphabet est vide.")

        for symbole in self.alphabet:
            if len(symbole) != 1:
                raise ValueError(
                    f"Le symbole « {symbole} » doit être un seul caractère "
                    "(séparer les symboles par des virgules)."
                )

        if self.etat_initial not in self.etats:
            raise ValueError(f"L'état initial « {self.etat_initial} » n'est pas dans l'ensemble des états.")

        for etat in self.etats_finaux:
            if etat not in self.etats:
                raise ValueError(f"L'état final « {etat} » n'est pas dans l'ensemble des états.")

        for etat, lignes in self.transitions.items():
            if etat not in self.etats:
                raise ValueError(f"Transition depuis l'état inconnu « {etat} ».")
            for symbole, destination in lignes.items():
                if symbole not in self.alphabet:
                    raise ValueError(f"Le symbole « {symbole} » (état {etat}) n'est pas dans l'alphabet.")
                if destination not in self.etats:
                    raise ValueError(f"La destination « {destination} » (état {etat}) n'est pas un état connu.")

        # Dans un AFD, il y a une transition pour chaque état et chaque symbole.
        for etat in sorted(self.etats):
            for symbole in sorted(self.alphabet):
                if symbole not in self.transitions.get(etat, {}):
                    raise ValueError(f"Transition manquante : delta({etat}, {symbole}) n'est pas définie.")

    # ------------------------------------------------------------------
    # Livrable 2 : reconnaissance d'un mot
    # ------------------------------------------------------------------

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
    """Écrit le chemin parcouru, une transition par ligne : 'q0 --a--> q1'."""
    if mot == "":
        return f"{chemin[0]}  (mot vide : aucune transition)"

    lignes = []
    for i, symbole in enumerate(mot):
        lignes.append(f"{chemin[i]} --{symbole}--> {chemin[i + 1]}")
    return "\n".join(lignes)


# ----------------------------------------------------------------------
# Lecture des textes saisis par l'utilisateur
# ----------------------------------------------------------------------

def separer(texte):
    """Transforme 'q0, q1 q2' en ['q0', 'q1', 'q2'] (virgules ou espaces)."""
    return texte.replace(",", " ").split()


def lire_transitions(texte):
    """Transforme le texte (une transition par ligne : 'q0 a q1') en dictionnaire."""
    transitions = {}
    for numero, ligne in enumerate(texte.splitlines(), start=1):
        if ligne.strip() == "":
            continue

        morceaux = ligne.split()
        if len(morceaux) != 3:
            raise ValueError(f"Ligne {numero} : écrire « état symbole destination » (exemple : q0 a q1).")

        etat, symbole, destination = morceaux
        if etat not in transitions:
            transitions[etat] = {}
        if symbole in transitions[etat]:
            raise ValueError(
                f"Ligne {numero} : delta({etat}, {symbole}) est déjà définie "
                "(un AFD n'a qu'une seule transition par symbole)."
            )
        transitions[etat][symbole] = destination
    return transitions


def creer_afd(texte_etats, texte_alphabet, texte_initial, texte_finaux, texte_transitions):
    """Construit un AFD à partir des textes saisis. Lève ValueError si c'est incorrect."""
    return AFD(
        set(separer(texte_etats)),
        set(separer(texte_alphabet)),
        texte_initial.strip(),
        set(separer(texte_finaux)),
        lire_transitions(texte_transitions),
    )
