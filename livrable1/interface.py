import tkinter as tk

import graphviz

from afd import creer_afd
from visualisation import dessiner

# Valeurs proposées au départ (l'automate « mots qui se terminent par ab »).
ETATS = "q0, q1, q2"
ALPHABET = "a, b"
INITIAL = "q0"
FINAUX = "q2"
TRANSITIONS = "q0 a q1\nq0 b q0\nq1 a q1\nq1 b q2\nq2 a q1\nq2 b q0"


class Application:
    def __init__(self, fenetre):
        fenetre.title("Automate fini déterministe - Livrable 1")
        self.fenetre = fenetre
        self.image = None  

        self.construire_saisie()
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
        sous_cadre = tk.Frame(cadre)
        sous_cadre.grid(row=ligne, column=0, sticky="w")
        tk.Label(sous_cadre, text=texte).pack(anchor="w")
        champ = tk.Entry(sous_cadre, width=38)
        champ.insert(0, valeur)
        champ.pack(anchor="w")
        return champ

    def construire_dessin(self):
        cadre = tk.LabelFrame(self.fenetre, text="Dessin de l'automate", padx=8, pady=8)
        cadre.grid(row=0, column=1, sticky="n", padx=8, pady=8)

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

        self.image = tk.PhotoImage(data=png)
        self.etiquette_dessin.config(image=self.image, width=self.image.width(), height=self.image.height())
        self.message.config(text="Automate créé : toutes les vérifications sont passées.", fg="green")


if __name__ == "__main__":
    fenetre = tk.Tk()
    Application(fenetre)
    fenetre.mainloop()
