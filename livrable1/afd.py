class AFD:
    def __init__(self, etats, alphabet, etat_initial, etats_finaux, transitions):
        self.etats = etats                  
        self.alphabet = alphabet           
        self.etat_initial = etat_initial   
        self.etats_finaux = etats_finaux   
        self.transitions = transitions     
        self.verifier()

    def verifier(self):
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
                
        for etat in sorted(self.etats):
            for symbole in sorted(self.alphabet):
                if symbole not in self.transitions.get(etat, {}):
                    raise ValueError(f"Transition manquante : delta({etat}, {symbole}) n'est pas définie.")


# ----------------------------------------------------------------------
# Lecture des textes saisis par l'utilisateur
# ----------------------------------------------------------------------

def separer(texte):
    return texte.replace(",", " ").split()


def lire_transitions(texte):
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
    return AFD(
        set(separer(texte_etats)),
        set(separer(texte_alphabet)),
        texte_initial.strip(),
        set(separer(texte_finaux)),
        lire_transitions(texte_transitions),
    )
