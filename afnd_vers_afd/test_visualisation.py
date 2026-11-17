"""Tests unitaires de visualisation.py : le texte du graphe Graphviz et l'image PNG."""

import unittest

import graphviz

from afnd import creer_afnd
from conversion import construire_afd
from exemple import afnd_cours
from visualisation import ajouter_fleche, creer_graphe, dessiner_afd, dessiner_afnd


def lignes_du_graphe(graphe):
    """Les lignes du texte DOT, sans l'indentation."""
    return [ligne.strip() for ligne in graphe.source.splitlines()]


class TestAjouterFleche(unittest.TestCase):
    def test_cree_la_fleche(self):
        fleches = {}
        ajouter_fleche(fleches, "A", "B", "a")
        self.assertEqual(fleches, {("A", "B"): ["a"]})

    def test_ajoute_un_symbole_sur_la_meme_fleche(self):
        fleches = {}
        ajouter_fleche(fleches, "A", "B", "a")
        ajouter_fleche(fleches, "A", "B", "b")
        self.assertEqual(fleches, {("A", "B"): ["a", "b"]})

    def test_fleches_differentes_restent_separees(self):
        fleches = {}
        ajouter_fleche(fleches, "A", "B", "a")
        ajouter_fleche(fleches, "A", "C", "b")
        ajouter_fleche(fleches, "B", "A", "a")
        self.assertEqual(len(fleches), 3)

    def test_le_sens_compte(self):
        fleches = {}
        ajouter_fleche(fleches, "A", "B", "a")
        ajouter_fleche(fleches, "B", "A", "a")
        self.assertIn(("A", "B"), fleches)
        self.assertIn(("B", "A"), fleches)

    def test_boucle(self):
        fleches = {}
        ajouter_fleche(fleches, "A", "A", "a")
        self.assertEqual(fleches, {("A", "A"): ["a"]})


class TestCreerGraphe(unittest.TestCase):
    def setUp(self):
        self.graphe = creer_graphe(
            {"0", "1"}, "0", {"1"},
            {("0", "1"): ["a", "b"], ("1", "1"): ["a"]},
            {"0": "zero", "1": "un"},
        )
        self.lignes = lignes_du_graphe(self.graphe)

    def test_est_un_graphe_oriente_de_gauche_a_droite(self):
        self.assertTrue(self.lignes[0].startswith("digraph"))
        self.assertIn("rankdir=LR", self.graphe.source)

    def test_utilise_les_libelles(self):
        self.assertIn("label=zero", self.graphe.source)
        self.assertIn("label=un", self.graphe.source)

    def test_etat_final_a_un_double_contour(self):
        ligne_1 = [ligne for ligne in self.lignes if ligne.startswith("1 [")][0]
        self.assertIn("peripheries=2", ligne_1)

    def test_etat_non_final_a_un_seul_contour(self):
        ligne_0 = [ligne for ligne in self.lignes if ligne.startswith("0 [")][0]
        self.assertNotIn("peripheries", ligne_0)

    def test_fleche_d_entree_vers_l_etat_initial(self):
        self.assertIn("__debut__ -> 0", self.lignes)

    def test_noeud_de_depart_est_un_point(self):
        self.assertIn("__debut__ [shape=point]", self.lignes)

    def test_symboles_d_une_meme_fleche_sont_regroupes(self):
        self.assertIn('0 -> 1 [label="a, b"]', self.lignes)

    def test_boucle(self):
        self.assertIn("1 -> 1 [label=a]", self.lignes)

    def test_format_png(self):
        self.assertEqual(self.graphe.format, "png")


class TestDessinerAFND(unittest.TestCase):
    def test_un_noeud_par_etat(self):
        graphe = dessiner_afnd(afnd_cours)
        lignes = lignes_du_graphe(graphe)
        for etat in afnd_cours.etats:
            self.assertTrue(any(ligne.startswith(f"{etat} [") for ligne in lignes), f"état {etat}")

    def test_etat_final_10_a_un_double_contour(self):
        lignes = lignes_du_graphe(dessiner_afnd(afnd_cours))
        ligne_10 = [ligne for ligne in lignes if ligne.startswith("10 [")][0]
        self.assertIn("peripheries=2", ligne_10)

    def test_un_seul_etat_a_un_double_contour(self):
        self.assertEqual(dessiner_afnd(afnd_cours).source.count("peripheries=2"), 1)

    def test_fleche_vers_l_etat_initial(self):
        self.assertIn("__debut__ -> 0", lignes_du_graphe(dessiner_afnd(afnd_cours)))

    def test_epsilon_transition_etiquetee_epsilon(self):
        self.assertIn('0 -> 1 [label="ε"]', lignes_du_graphe(dessiner_afnd(afnd_cours)))

    def test_transition_normale(self):
        self.assertIn("2 -> 3 [label=a]", lignes_du_graphe(dessiner_afnd(afnd_cours)))

    def test_une_fleche_par_transition_du_cours(self):
        # 13 transitions dans la Fig. 2 + la flèche d'entrée
        graphe = dessiner_afnd(afnd_cours)
        nombre_de_fleches = sum(1 for ligne in lignes_du_graphe(graphe) if " -> " in ligne)
        self.assertEqual(nombre_de_fleches, 13 + 1)

    def test_regroupe_epsilon_et_symbole_entre_les_memes_etats(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 a 1\n0 eps 1")
        self.assertIn('0 -> 1 [label="a, ε"]', lignes_du_graphe(dessiner_afnd(afnd)))

    def test_non_determinisme_donne_deux_fleches(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 1\n0 a 2")
        lignes = lignes_du_graphe(dessiner_afnd(afnd))
        self.assertIn("0 -> 1 [label=a]", lignes)
        self.assertIn("0 -> 2 [label=a]", lignes)

    def test_afnd_sans_transition(self):
        afnd = creer_afnd("0", "a", "0", "", "")
        graphe = dessiner_afnd(afnd)
        self.assertEqual(sum(1 for ligne in lignes_du_graphe(graphe) if " -> " in ligne), 1)

    def test_boucle(self):
        afnd = creer_afnd("0", "a", "0", "0", "0 a 0")
        self.assertIn("0 -> 0 [label=a]", lignes_du_graphe(dessiner_afnd(afnd)))


class TestDessinerAFD(unittest.TestCase):
    def setUp(self):
        self.afd, self.noms, self.etapes = construire_afd(afnd_cours)
        self.graphe = dessiner_afd(self.afd)
        self.lignes = lignes_du_graphe(self.graphe)

    def test_un_noeud_par_etat(self):
        for etat in ["A", "B", "C", "D", "E"]:
            self.assertTrue(any(ligne.startswith(f"{etat} [") for ligne in self.lignes), f"état {etat}")

    def test_le_libelle_est_le_nom_de_l_etat(self):
        self.assertIn("A [label=A shape=ellipse]", self.lignes)

    def test_seul_e_a_un_double_contour(self):
        self.assertEqual(self.graphe.source.count("peripheries=2"), 1)
        ligne_e = [ligne for ligne in self.lignes if ligne.startswith("E [")][0]
        self.assertIn("peripheries=2", ligne_e)

    def test_fleche_vers_l_etat_initial(self):
        self.assertIn("__debut__ -> A", self.lignes)

    def test_transitions_de_l_etat_a(self):
        self.assertIn("A -> B [label=a]", self.lignes)
        self.assertIn("A -> C [label=b]", self.lignes)

    def test_boucles_du_cours(self):
        self.assertIn("B -> B [label=a]", self.lignes)
        self.assertIn("C -> C [label=b]", self.lignes)

    def test_transitions_vers_b(self):
        for source in ["C", "D", "E"]:
            self.assertIn(f"{source} -> B [label=a]", self.lignes)

    def test_nombre_de_fleches(self):
        # 5 états x 2 symboles = 10 transitions, aucune ne se regroupe + la flèche d'entrée
        nombre_de_fleches = sum(1 for ligne in self.lignes if " -> " in ligne)
        self.assertEqual(nombre_de_fleches, 10 + 1)

    def test_regroupe_les_symboles_menant_au_meme_etat(self):
        afnd = creer_afnd("0", "a, b", "0", "0", "0 a 0\n0 b 0")
        afd, noms, etapes = construire_afd(afnd)
        self.assertIn('A -> A [label="a, b"]', lignes_du_graphe(dessiner_afd(afd)))

    def test_etat_puits_dessine(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        lignes = lignes_du_graphe(dessiner_afd(afd))
        self.assertIn('C -> C [label="a, b"]', lignes)


class TestImagePNG(unittest.TestCase):
    """Ces tests ont besoin du programme Graphviz (commande « dot »)."""

    def produire_png(self, graphe):
        try:
            return graphe.pipe()
        except graphviz.ExecutableNotFound:
            self.skipTest("Graphviz (commande « dot ») n'est pas installé")

    def test_afnd_donne_une_image_png(self):
        png = self.produire_png(dessiner_afnd(afnd_cours))
        self.assertTrue(png.startswith(b"\x89PNG"))

    def test_afd_donne_une_image_png(self):
        afd, noms, etapes = construire_afd(afnd_cours)
        png = self.produire_png(dessiner_afd(afd))
        self.assertTrue(png.startswith(b"\x89PNG"))

    def test_image_non_vide(self):
        png = self.produire_png(dessiner_afnd(afnd_cours))
        self.assertGreater(len(png), 500)

    def test_automate_a_un_seul_etat(self):
        afnd = creer_afnd("0", "a", "0", "0", "0 a 0")
        png = self.produire_png(dessiner_afnd(afnd))
        self.assertTrue(png.startswith(b"\x89PNG"))

    def test_afd_de_32_etats(self):
        lignes = ["0 a 0", "0 b 0", "0 a 1"]
        for i in range(1, 5):
            lignes.append(f"{i} a {i + 1}")
            lignes.append(f"{i} b {i + 1}")
        afnd = creer_afnd("0, 1, 2, 3, 4, 5", "a, b", "0", "5", "\n".join(lignes))
        afd, noms, etapes = construire_afd(afnd)
        png = self.produire_png(dessiner_afd(afd))
        self.assertTrue(png.startswith(b"\x89PNG"))

    def test_noms_d_etats_avec_lettres(self):
        afnd = creer_afnd("debut, fin", "a", "debut", "fin", "debut a fin")
        png = self.produire_png(dessiner_afnd(afnd))
        self.assertTrue(png.startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()
