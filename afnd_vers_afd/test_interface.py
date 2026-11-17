"""Tests de l'interface graphique (interface.py).

La fenêtre est créée mais cachée. Si aucun écran n'est disponible (serveur sans affichage),
tous ces tests sont ignorés.
"""

import tkinter as tk
import unittest
from unittest import mock

import graphviz

import interface
from interface import Application


def remplir(champ, texte):
    """Remplace le contenu d'une zone de saisie (Entry)."""
    champ.delete(0, "end")
    champ.insert(0, texte)


def remplir_texte(zone, texte):
    """Remplace le contenu d'une zone de texte (Text)."""
    zone.delete("1.0", "end")
    zone.insert("1.0", texte)


def graphviz_est_installe():
    try:
        graphviz.Digraph().pipe(format="png")
        return True
    except graphviz.ExecutableNotFound:
        return False


class BaseInterface(unittest.TestCase):
    def setUp(self):
        try:
            self.fenetre = tk.Tk()
        except tk.TclError:
            self.skipTest("Pas d'écran disponible pour Tkinter")
        self.fenetre.withdraw()
        self.app = Application(self.fenetre)

    def tearDown(self):
        if hasattr(self, "fenetre"):
            self.fenetre.destroy()

    def saisir_et_tester(self, mot):
        remplir(self.app.champ_mot, mot)
        self.app.tester_mot()
        return self.app.resultat.cget("text")

    def chemin(self):
        return self.app.zone_chemin.get("1.0", "end").strip()


class TestDebut(BaseInterface):
    def test_valeurs_proposees_au_depart(self):
        self.assertEqual(self.app.champ_alphabet.get(), "a, b")
        self.assertEqual(self.app.champ_initial.get(), "0")
        self.assertEqual(self.app.champ_finaux.get(), "10")

    def test_les_transitions_proposees_sont_celles_du_cours(self):
        texte = self.app.champ_transitions.get("1.0", "end")
        self.assertEqual(len([ligne for ligne in texte.splitlines() if ligne.strip()]), 13)

    def test_aucun_afd_au_depart(self):
        self.assertIsNone(self.app.afd)

    def test_tester_un_mot_avant_la_conversion(self):
        texte = self.saisir_et_tester("ab")
        self.assertIn("Convertissez d'abord", texte)
        self.assertEqual(self.app.resultat.cget("fg"), "red")

    def test_le_message_est_vide_au_depart(self):
        self.assertEqual(self.app.message.cget("text"), "")


@unittest.skipUnless(graphviz_est_installe(), "Graphviz (commande « dot ») n'est pas installé")
class TestConversion(BaseInterface):
    def test_conversion_de_l_exemple_du_cours(self):
        self.app.convertir()
        self.assertIsNotNone(self.app.afd)
        self.assertEqual(len(self.app.afd.etats), 5)

    def test_message_de_reussite_en_vert(self):
        self.app.convertir()
        self.assertIn("11 états converti en AFD de 5 états", self.app.message.cget("text"))
        self.assertEqual(self.app.message.cget("fg"), "green")

    def test_les_deux_images_sont_affichees(self):
        self.app.convertir()
        self.assertGreater(self.app.image_afnd.width(), 100)
        self.assertGreater(self.app.image_afd.width(), 100)

    def test_la_zone_de_texte_contient_la_table_et_les_etapes(self):
        self.app.convertir()
        texte = self.app.zone_texte.get("1.0", "end")
        self.assertIn("{0, 1, 2, 4, 7}", texte)
        self.assertIn("Étapes de l'algorithme", texte)
        self.assertIn("Traitement de T", texte)

    def test_convertir_deux_fois_ne_duplique_pas_le_texte(self):
        self.app.convertir()
        premier = self.app.zone_texte.get("1.0", "end")
        self.app.convertir()
        self.assertEqual(self.app.zone_texte.get("1.0", "end"), premier)

    def test_autre_automate(self):
        remplir(self.app.champ_etats, "0, 1, 2")
        remplir(self.app.champ_finaux, "2")
        remplir_texte(self.app.champ_transitions, "0 a 1\n1 a 1\n1 a 2\n2 b 0\n1 eps 0")
        self.app.convertir()
        self.assertEqual(len(self.app.afd.etats), 4)
        self.assertIn("3 états converti en AFD de 4 états", self.app.message.cget("text"))

    def test_symbole_hors_alphabet_donne_un_message_d_erreur(self):
        remplir_texte(self.app.champ_transitions, "0 z 1")
        self.app.convertir()
        self.assertEqual(self.app.message.cget("fg"), "red")
        self.assertIn("alphabet", self.app.message.cget("text"))
        self.assertIsNone(self.app.afd)

    def test_etat_initial_inconnu_donne_un_message_d_erreur(self):
        remplir(self.app.champ_initial, "99")
        self.app.convertir()
        self.assertEqual(self.app.message.cget("fg"), "red")
        self.assertIn("initial", self.app.message.cget("text"))

    def test_etat_final_inconnu_donne_un_message_d_erreur(self):
        remplir(self.app.champ_finaux, "99")
        self.app.convertir()
        self.assertIn("final", self.app.message.cget("text"))

    def test_transition_mal_ecrite_donne_le_numero_de_ligne(self):
        remplir_texte(self.app.champ_transitions, "0 a 1\nmauvaise ligne")
        self.app.convertir()
        self.assertIn("Ligne 2", self.app.message.cget("text"))

    def test_alphabet_sans_virgule_donne_un_message_d_erreur(self):
        remplir(self.app.champ_alphabet, "ab")
        self.app.convertir()
        self.assertIn("un seul caractère", self.app.message.cget("text"))

    def test_une_erreur_ne_plante_pas_le_programme(self):
        remplir(self.app.champ_etats, "")
        self.app.convertir()
        self.assertEqual(self.app.message.cget("fg"), "red")

    def test_apres_une_erreur_on_peut_reconvertir(self):
        remplir(self.app.champ_initial, "99")
        self.app.convertir()
        remplir(self.app.champ_initial, "0")
        self.app.convertir()
        self.assertEqual(self.app.message.cget("fg"), "green")
        self.assertIsNotNone(self.app.afd)

    def test_une_erreur_garde_l_ancien_afd(self):
        self.app.convertir()
        ancien = self.app.afd
        remplir(self.app.champ_initial, "99")
        self.app.convertir()
        self.assertIs(self.app.afd, ancien)

    def test_graphviz_absent_donne_un_message_clair(self):
        erreur = graphviz.ExecutableNotFound(["dot"])
        with mock.patch.object(interface, "dessiner_afnd", side_effect=erreur):
            self.app.convertir()
        self.assertEqual(self.app.message.cget("fg"), "red")
        self.assertIn("Graphviz", self.app.message.cget("text"))

    def test_saisie_avec_epsilon_ecrit_eps(self):
        remplir(self.app.champ_etats, "0, 1")
        remplir(self.app.champ_finaux, "1")
        remplir_texte(self.app.champ_transitions, "0 eps 1")
        self.app.convertir()
        self.assertTrue(self.app.afd.reconnaitre("")[0])


@unittest.skipUnless(graphviz_est_installe(), "Graphviz (commande « dot ») n'est pas installé")
class TestTesterUnMot(BaseInterface):
    def setUp(self):
        super().setUp()
        self.app.convertir()  # AFD du cours : mots qui se terminent par abb

    def test_mot_accepte(self):
        self.assertEqual(self.saisir_et_tester("aabb"), "Mot accepté")
        self.assertEqual(self.app.resultat.cget("fg"), "green")

    def test_mot_rejete(self):
        self.assertEqual(self.saisir_et_tester("ab"), "Mot rejeté")
        self.assertEqual(self.app.resultat.cget("fg"), "red")

    def test_mot_vide(self):
        self.assertEqual(self.saisir_et_tester(""), "Mot rejeté")
        self.assertIn("mot vide", self.chemin())

    def test_chemin_d_un_mot_accepte(self):
        self.saisir_et_tester("aabb")
        lignes = self.chemin().splitlines()
        self.assertEqual(lignes[:4], ["A --a--> B", "B --a--> B", "B --b--> D", "D --b--> E"])
        self.assertIn("État atteint : E (état final)", lignes[-1])

    def test_chemin_d_un_mot_rejete(self):
        self.saisir_et_tester("ab")
        lignes = self.chemin().splitlines()
        self.assertEqual(lignes[:2], ["A --a--> B", "B --b--> D"])
        self.assertIn("D (état non final)", lignes[-1])

    def test_symbole_hors_alphabet(self):
        texte = self.saisir_et_tester("abc")
        self.assertIn("rejeté", texte)
        self.assertIn("« c »", texte)
        self.assertEqual(self.app.resultat.cget("fg"), "red")

    def test_plusieurs_symboles_hors_alphabet(self):
        texte = self.saisir_et_tester("xyz")
        self.assertIn("« x »", texte)
        self.assertIn("« y »", texte)
        self.assertIn("« z »", texte)

    def test_pas_de_chemin_pour_un_symbole_invalide(self):
        self.saisir_et_tester("abc")
        self.assertIn("aucun chemin", self.chemin())

    def test_espaces_autour_du_mot_sont_ignores(self):
        self.assertEqual(self.saisir_et_tester("  abb  "), "Mot accepté")

    def test_le_chemin_est_remplace_a_chaque_test(self):
        self.saisir_et_tester("aabb")
        self.saisir_et_tester("a")
        lignes = self.chemin().splitlines()
        self.assertEqual(lignes[0], "A --a--> B")
        self.assertEqual(len(lignes), 2)

    def test_le_resultat_change_a_chaque_test(self):
        self.assertEqual(self.saisir_et_tester("abb"), "Mot accepté")
        self.assertEqual(self.saisir_et_tester("abba"), "Mot rejeté")
        self.assertEqual(self.saisir_et_tester("abb"), "Mot accepté")

    def test_touche_entree_est_liee_au_test(self):
        self.assertTrue(self.app.champ_mot.bind("<Return>"))

    def test_le_test_utilise_le_dernier_afd_converti(self):
        remplir(self.app.champ_etats, "0, 1")
        remplir(self.app.champ_alphabet, "a")
        remplir(self.app.champ_finaux, "1")
        remplir_texte(self.app.champ_transitions, "0 a 1\n1 a 1")
        self.app.convertir()
        self.assertEqual(self.saisir_et_tester("aaa"), "Mot accepté")
        self.assertEqual(self.saisir_et_tester("b"), "Mot rejeté : symbole(s) hors de l'alphabet : « b »")

    def test_mot_tres_long(self):
        self.assertEqual(self.saisir_et_tester("ab" * 2000 + "b"), "Mot accepté")

    def test_tous_les_mots_jusqu_a_5_lettres(self):
        from itertools import product
        for longueur in range(0, 6):
            for lettres in product("ab", repeat=longueur):
                mot = "".join(lettres)
                attendu = "Mot accepté" if mot.endswith("abb") else "Mot rejeté"
                self.assertEqual(self.saisir_et_tester(mot), attendu, f"mot '{mot}'")


if __name__ == "__main__":
    unittest.main()
