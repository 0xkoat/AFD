import tkinter as tk

import graphviz

from afnd import creer_afnd
from afd import formater_chemin
from conversion import construire_afd, table_afd
from visualisation import dessiner_afd, dessiner_afnd

ETATS = "0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
ALPHABET = "a, b"
INITIAL = "0"
FINAUX = "10"
TRANSITIONS = """0 ε 1
0 ε 7
1 ε 2
1 ε 4
2 a 3
3 ε 6
4 b 5
5 ε 6
6 ε 1
6 ε 7
7 a 8
8 b 9
9 b 10"""


class Application:
    def __init__(self, fenetre):
        fenetre.title("Conversion AFND -> AFD (construction des sous-ensembles)")
        self.fenetre = fenetre
        self.image_afnd = None  
        self.image_afd = None
        self.afd = None  # l'AFD obtenu par la dernière conversion (None avant)

        self.construire_saisie()
        self.construire_resultat()
        self.construire_test()
        fenetre.rowconfigure(1, weight=1) 

    # ------------------------------------------------------------------
    # Construction de la fenêtre
    # ------------------------------------------------------------------

    def construire_saisie(self):
        cadre = tk.LabelFrame(self.fenetre, text="AFND à convertir", padx=8, pady=8)
        cadre.grid(row=0, column=0, rowspan=2, sticky="n", padx=8, pady=8)

        self.champ_etats = self.ajouter_champ(cadre, "États (séparés par des virgules)", ETATS)
        self.champ_alphabet = self.ajouter_champ(cadre, "Alphabet (sans ε)", ALPHABET)
        self.champ_initial = self.ajouter_champ(cadre, "État initial", INITIAL)
        self.champ_finaux = self.ajouter_champ(cadre, "États finaux (séparés par des virgules)", FINAUX)

        tk.Label(cadre, text="Transitions : une par ligne « état symbole destination »").pack(anchor="w", pady=(8, 0))
        tk.Label(cadre, text="(ε = transition vide, on peut écrire eps)").pack(anchor="w")
        self.champ_transitions = tk.Text(cadre, width=30, height=14)
        self.champ_transitions.insert("1.0", TRANSITIONS)
        self.champ_transitions.pack(anchor="w")

        tk.Button(cadre, text="Convertir en AFD", command=self.convertir).pack(pady=8)

        self.message = tk.Label(cadre, text="", wraplength=260, justify="left")
        self.message.pack(anchor="w")

    def ajouter_champ(self, cadre, texte, valeur):
        """Ajoute un titre suivi d'une zone de saisie, et retourne la zone de saisie."""
        tk.Label(cadre, text=texte).pack(anchor="w")
        champ = tk.Entry(cadre, width=34)
        champ.insert(0, valeur)
        champ.pack(anchor="w")
        return champ

    def construire_resultat(self):
        cadre_afnd = tk.LabelFrame(self.fenetre, text="AFND (entrée)", padx=8, pady=8)
        cadre_afnd.grid(row=0, column=1, sticky="n", padx=8, pady=8)
        self.dessin_afnd = tk.Label(cadre_afnd, text="", width=60, height=15)
        self.dessin_afnd.pack()

        cadre_afd = tk.LabelFrame(self.fenetre, text="AFD (résultat)", padx=8, pady=8)
        cadre_afd.grid(row=0, column=2, sticky="n", padx=8, pady=8)
        self.dessin_afd = tk.Label(cadre_afd, text="", width=60, height=15)
        self.dessin_afd.pack()

        cadre_texte = tk.LabelFrame(self.fenetre, text="Table de transitions de l'AFD et étapes de l'algorithme", padx=8, pady=8)
        cadre_texte.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=8, pady=8)
        self.zone_texte = tk.Text(cadre_texte, width=110, height=10, font=("Courier", 10))
        barre = tk.Scrollbar(cadre_texte, command=self.zone_texte.yview)
        self.zone_texte.config(yscrollcommand=barre.set)
        self.zone_texte.pack(side="left", fill="both", expand=True)
        barre.pack(side="right", fill="y")

    def construire_test(self):
        cadre = tk.LabelFrame(self.fenetre, text="Tester un mot avec l'AFD obtenu", padx=8, pady=8)
        cadre.grid(row=2, column=0, columnspan=3, sticky="ew", padx=8, pady=8)

        gauche = tk.Frame(cadre)
        gauche.pack(side="left", anchor="n")
        tk.Label(gauche, text="Mot à tester (laisser vide pour le mot vide)").pack(anchor="w")
        self.champ_mot = tk.Entry(gauche, width=34)
        self.champ_mot.pack(anchor="w")
        self.champ_mot.bind("<Return>", lambda evenement: self.tester_mot())
        tk.Button(gauche, text="Tester le mot", command=self.tester_mot).pack(anchor="w", pady=8)

        milieu = tk.Frame(cadre)
        milieu.pack(side="left", anchor="n", padx=30)
        self.resultat = tk.Label(milieu, text="", font=("Arial", 12, "bold"), wraplength=320, justify="left")
        self.resultat.pack(anchor="w")

        tk.Label(cadre, text="Chemin parcouru dans l'AFD :").pack(side="top", anchor="w")
        self.zone_chemin = tk.Text(cadre, width=40, height=5, font=("Courier", 10))
        self.zone_chemin.pack(side="top", anchor="w")

    # ------------------------------------------------------------------
    # Action : convertir
    # ------------------------------------------------------------------

    def convertir(self):
        try:
            afnd = creer_afnd(
                self.champ_etats.get(),
                self.champ_alphabet.get(),
                self.champ_initial.get(),
                self.champ_finaux.get(),
                self.champ_transitions.get("1.0", "end"),
            )
            afd, noms, etapes = construire_afd(afnd)
            png_afnd = dessiner_afnd(afnd).pipe()
            png_afd = dessiner_afd(afd).pipe()
        except ValueError as erreur:
            self.message.config(text=str(erreur), fg="red")
            return
        except graphviz.ExecutableNotFound:
            self.message.config(text="Graphviz n'est pas installé (commande « dot » introuvable).", fg="red")
            return

        self.afd = afd
        self.image_afnd = tk.PhotoImage(data=png_afnd)
        self.dessin_afnd.config(image=self.image_afnd, width=self.image_afnd.width(), height=self.image_afnd.height())
        self.image_afd = tk.PhotoImage(data=png_afd)
        self.dessin_afd.config(image=self.image_afd, width=self.image_afd.width(), height=self.image_afd.height())

        texte = table_afd(afd, noms) + "\n\n\nÉtapes de l'algorithme :\n" + "\n".join(etapes)
        self.zone_texte.delete("1.0", "end")
        self.zone_texte.insert("1.0", texte)

        self.message.config(text=f"AFND de {len(afnd.etats)} états converti en AFD de {len(afd.etats)} états.", fg="green")

    # ------------------------------------------------------------------
    # Action : tester un mot
    # ------------------------------------------------------------------

    def tester_mot(self):
        if self.afd is None:
            self.resultat.config(text="Convertissez d'abord l'AFND en AFD.", fg="red")
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
                nature = "état final"
            else:
                self.resultat.config(text="Mot rejeté", fg="red")
                nature = "état non final"
            texte_chemin = formater_chemin(mot, chemin) + f"\nÉtat atteint : {chemin[-1]} ({nature})"

        self.zone_chemin.delete("1.0", "end")
        self.zone_chemin.insert("1.0", texte_chemin)


if __name__ == "__main__":
    fenetre = tk.Tk()
    Application(fenetre)
    fenetre.mainloop()
