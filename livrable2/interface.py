"""Livrables 1 et 2 - Interface graphique : saisie de l'AFD, visualisation et test de mots.

Lancer :  python interface.py
"""

import tkinter as tk

import graphviz

from afd import creer_afd, formater_chemin
from visualisation import dessiner

# Valeurs proposées au départ (l'automate « mots qui se terminent par ab »).
ETATS = "q0, q1, q2"
ALPHABET = "a, b"
INITIAL = "q0"
FINAUX = "q2"
TRANSITIONS = "q0 a q1\nq0 b q0\nq1 a q1\nq1 b q2\nq2 a q1\nq2 b q0"


class Application:
    def __init__(self, fenetre):
        fenetre.title("Automate fini déterministe - Livrable 2")
        self.fenetre = fenetre
        self.afd = None    # l'automate créé (None tant qu'il n'est pas créé)
        self.image = None  # on garde l'image ici, sinon Tkinter la supprime

        self.construire_saisie()
        self.construire_test()
        self.construire_dessin()

    # ------------------------------------------------------------------
    # Construction de la fenêtre
    # ------------------------------------------------------------------

    def construire_saisie(self):
        cadre = tk.LabelFrame(self.fenetre, text="Définition de l'automate", padx=8, pady=8)
        cadre.grid(row=0, column=0, sticky="n", padx=8, pady=8)

        self.champ_etats = self.ajouter_champ(cadre, "États (séparés par des virgules)", 0, ETATS)
        self.champ_alphabet = self.ajouter_champ(cadre, "Alphabet (séparé par des virgules)", 1, ALPHABET)
        self.champ_initial = self.ajouter_champ(cadre, "État initial", 2, INITIAL)
        self.champ_finaux = self.ajouter_champ(cadre, "États finaux (séparés par des virgules)", 3, FINAUX)

        tk.Label(cadre, text="Transitions (une par ligne : état symbole destination)").grid(
            row=4, column=0, sticky="w", pady=(8, 0)
        )
        self.champ_transitions = tk.Text(cadre, width=35, height=10)
        self.champ_transitions.insert("1.0", TRANSITIONS)
        self.champ_transitions.grid(row=5, column=0, sticky="w")

        tk.Button(cadre, text="Créer et dessiner l'automate", command=self.creer_automate).grid(
            row=6, column=0, pady=8
        )

        self.message = tk.Label(cadre, text="", wraplength=300, justify="left")
        self.message.grid(row=7, column=0, sticky="w")

    def ajouter_champ(self, cadre, texte, ligne, valeur):
        """Ajoute un titre suivi d'une zone de saisie, et retourne la zone de saisie."""
        sous_cadre = tk.Frame(cadre)
        sous_cadre.grid(row=ligne, column=0, sticky="w")
        tk.Label(sous_cadre, text=texte).pack(anchor="w")
        champ = tk.Entry(sous_cadre, width=38)
        champ.insert(0, valeur)
        champ.pack(anchor="w")
        return champ

    def construire_test(self):
        cadre = tk.LabelFrame(self.fenetre, text="Tester un mot", padx=8, pady=8)
        cadre.grid(row=1, column=0, sticky="n", padx=8, pady=8)

        tk.Label(cadre, text="Mot à tester (laisser vide pour tester le mot vide)").pack(anchor="w")
        self.champ_mot = tk.Entry(cadre, width=38)
        self.champ_mot.pack(anchor="w")
        self.champ_mot.bind("<Return>", lambda evenement: self.tester_mot())

        tk.Button(cadre, text="Tester le mot", command=self.tester_mot).pack(pady=8)

        self.resultat = tk.Label(cadre, text="", font=("Arial", 12, "bold"), wraplength=300, justify="left")
        self.resultat.pack(anchor="w")

        tk.Label(cadre, text="Chemin parcouru :").pack(anchor="w", pady=(8, 0))
        self.zone_chemin = tk.Text(cadre, width=35, height=8)
        self.zone_chemin.pack(anchor="w")

    def construire_dessin(self):
        cadre = tk.LabelFrame(self.fenetre, text="Dessin de l'automate", padx=8, pady=8)
        cadre.grid(row=0, column=1, rowspan=2, sticky="n", padx=8, pady=8)

        self.etiquette_dessin = tk.Label(cadre, text="Cliquez sur « Créer et dessiner l'automate »", width=60, height=20)
        self.etiquette_dessin.pack()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def creer_automate(self):
        try:
            afd = creer_afd(
                self.champ_etats.get(),
                self.champ_alphabet.get(),
                self.champ_initial.get(),
                self.champ_finaux.get(),
                self.champ_transitions.get("1.0", "end"),
            )
            png = dessiner(afd).pipe()
        except ValueError as erreur:
            self.message.config(text=str(erreur), fg="red")
            return
        except graphviz.ExecutableNotFound:
            self.message.config(text="Graphviz n'est pas installé (commande « dot » introuvable).", fg="red")
            return

        self.afd = afd
        self.image = tk.PhotoImage(data=png)
        self.etiquette_dessin.config(image=self.image, width=self.image.width(), height=self.image.height())
        self.message.config(text="Automate créé : toutes les vérifications sont passées.", fg="green")

    def tester_mot(self):
        if self.afd is None:
            self.resultat.config(text="Créez d'abord l'automate.", fg="red")
            return

        mot = self.champ_mot.get().strip()
        accepte, chemin, symboles_invalides = self.afd.reconnaitre(mot)

        if len(symboles_invalides) > 0:
            texte_symboles = ", ".join(f"« {symbole} »" for symbole in symboles_invalides)
            self.resultat.config(text=f"Mot rejeté : symbole(s) hors de l'alphabet : {texte_symboles}", fg="red")
            texte_chemin = "(aucun chemin : la lecture n'a pas commencé)"
        else:
            if accepte:
                self.resultat.config(text="Mot accepté", fg="green")
            else:
                self.resultat.config(text="Mot rejeté", fg="red")
            etat_final = chemin[-1]
            if accepte:
                nature = "état final"
            else:
                nature = "état non final"
            texte_chemin = formater_chemin(mot, chemin) + f"\nÉtat atteint : {etat_final} ({nature})"

        self.zone_chemin.delete("1.0", "end")
        self.zone_chemin.insert("1.0", texte_chemin)


if __name__ == "__main__":
    fenetre = tk.Tk()
    Application(fenetre)
    fenetre.mainloop()
