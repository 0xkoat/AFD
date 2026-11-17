"""Tests unitaires de afnd.py : la classe AFND et la lecture des saisies."""

import unittest

from afnd import AFND, EPSILON, creer_afnd, lire_transitions, separer


def afnd_simple():
    """AFND de départ pour les tests : 0 -a-> 1, état final 1."""
    return AFND({"0", "1"}, {"a", "b"}, "0", {"1"}, {"0": {"a": {"1"}}})


class TestSeparer(unittest.TestCase):
    def test_virgules(self):
        self.assertEqual(separer("a,b,c"), ["a", "b", "c"])

    def test_virgules_et_espaces(self):
        self.assertEqual(separer("a, b, c"), ["a", "b", "c"])

    def test_espaces_seulement(self):
        self.assertEqual(separer("q0 q1 q2"), ["q0", "q1", "q2"])

    def test_melange_virgules_et_espaces(self):
        self.assertEqual(separer("q0, q1 q2,q3"), ["q0", "q1", "q2", "q3"])

    def test_texte_vide(self):
        self.assertEqual(separer(""), [])

    def test_espaces_seulement_donne_liste_vide(self):
        self.assertEqual(separer("     "), [])

    def test_virgules_seules(self):
        self.assertEqual(separer(",,,"), [])

    def test_virgules_en_double(self):
        self.assertEqual(separer("a,,b"), ["a", "b"])

    def test_espaces_au_debut_et_a_la_fin(self):
        self.assertEqual(separer("   a, b   "), ["a", "b"])

    def test_tabulation_et_retour_ligne(self):
        self.assertEqual(separer("a\tb\nc"), ["a", "b", "c"])

    def test_un_seul_element(self):
        self.assertEqual(separer("q0"), ["q0"])

    def test_noms_de_plusieurs_caracteres(self):
        self.assertEqual(separer("etat1, etat2"), ["etat1", "etat2"])

    def test_garde_les_doublons(self):
        self.assertEqual(separer("a, a"), ["a", "a"])

    def test_garde_epsilon(self):
        self.assertEqual(separer("a, ε"), ["a", "ε"])


class TestLireTransitions(unittest.TestCase):
    def test_une_transition(self):
        self.assertEqual(lire_transitions("0 a 1"), {"0": {"a": {"1"}}})

    def test_texte_vide(self):
        self.assertEqual(lire_transitions(""), {})

    def test_lignes_vides_ignorees(self):
        self.assertEqual(lire_transitions("\n\n0 a 1\n\n\n"), {"0": {"a": {"1"}}})

    def test_ligne_avec_espaces_seulement_ignoree(self):
        self.assertEqual(lire_transitions("   \n0 a 1\n  \t "), {"0": {"a": {"1"}}})

    def test_deux_symboles_differents(self):
        resultat = lire_transitions("0 a 1\n0 b 2")
        self.assertEqual(resultat, {"0": {"a": {"1"}, "b": {"2"}}})

    def test_non_determinisme_deux_destinations(self):
        resultat = lire_transitions("0 a 1\n0 a 2")
        self.assertEqual(resultat, {"0": {"a": {"1", "2"}}})

    def test_non_determinisme_trois_destinations(self):
        resultat = lire_transitions("0 a 1\n0 a 2\n0 a 3")
        self.assertEqual(resultat["0"]["a"], {"1", "2", "3"})

    def test_ligne_en_double_sans_effet(self):
        resultat = lire_transitions("0 a 1\n0 a 1")
        self.assertEqual(resultat, {"0": {"a": {"1"}}})

    def test_plusieurs_etats_sources(self):
        resultat = lire_transitions("0 a 1\n1 b 0")
        self.assertEqual(resultat, {"0": {"a": {"1"}}, "1": {"b": {"0"}}})

    def test_epsilon_ecrit_avec_le_caractere(self):
        self.assertEqual(lire_transitions("0 ε 1"), {"0": {EPSILON: {"1"}}})

    def test_epsilon_ecrit_eps(self):
        self.assertEqual(lire_transitions("0 eps 1"), {"0": {EPSILON: {"1"}}})

    def test_eps_et_epsilon_donnent_la_meme_cle(self):
        resultat = lire_transitions("0 eps 1\n0 ε 2")
        self.assertEqual(resultat, {"0": {EPSILON: {"1", "2"}}})

    def test_plusieurs_espaces_entre_les_mots(self):
        self.assertEqual(lire_transitions("0    a     1"), {"0": {"a": {"1"}}})

    def test_tabulations_entre_les_mots(self):
        self.assertEqual(lire_transitions("0\ta\t1"), {"0": {"a": {"1"}}})

    def test_retours_ligne_windows(self):
        resultat = lire_transitions("0 a 1\r\n1 b 0\r\n")
        self.assertEqual(resultat, {"0": {"a": {"1"}}, "1": {"b": {"0"}}})

    def test_noms_d_etats_de_plusieurs_caracteres(self):
        self.assertEqual(lire_transitions("q10 a q20"), {"q10": {"a": {"q20"}}})

    def test_boucle_sur_un_etat(self):
        self.assertEqual(lire_transitions("0 a 0"), {"0": {"a": {"0"}}})

    def test_erreur_deux_morceaux(self):
        with self.assertRaises(ValueError):
            lire_transitions("0 a")

    def test_erreur_un_morceau(self):
        with self.assertRaises(ValueError):
            lire_transitions("0")

    def test_erreur_quatre_morceaux(self):
        with self.assertRaises(ValueError):
            lire_transitions("0 a 1 2")

    def test_erreur_virgule_dans_destination_mal_formee(self):
        # « 0 a 1, 2 » fait 4 morceaux : il faut écrire une ligne par destination.
        with self.assertRaises(ValueError):
            lire_transitions("0 a 1, 2")

    def test_erreur_donne_le_numero_de_ligne(self):
        with self.assertRaisesRegex(ValueError, "Ligne 3"):
            lire_transitions("0 a 1\n1 b 0\nerreur ici pas bon")

    def test_numero_de_ligne_compte_les_lignes_vides(self):
        with self.assertRaisesRegex(ValueError, "Ligne 3"):
            lire_transitions("0 a 1\n\nmauvaise")

    def test_ne_modifie_pas_le_texte_d_une_autre_ligne(self):
        resultat = lire_transitions("0 a 1\n0 b 0\n1 a 1")
        self.assertEqual(resultat["0"], {"a": {"1"}, "b": {"0"}})
        self.assertEqual(resultat["1"], {"a": {"1"}})


class TestAFNDVerifier(unittest.TestCase):
    def test_automate_valide(self):
        afnd = afnd_simple()
        self.assertEqual(afnd.etat_initial, "0")

    def test_attributs_enregistres(self):
        afnd = afnd_simple()
        self.assertEqual(afnd.etats, {"0", "1"})
        self.assertEqual(afnd.alphabet, {"a", "b"})
        self.assertEqual(afnd.etat_initial, "0")
        self.assertEqual(afnd.etats_finaux, {"1"})
        self.assertEqual(afnd.transitions, {"0": {"a": {"1"}}})

    def test_sans_aucune_transition_est_valide(self):
        AFND({"0"}, {"a"}, "0", set(), {})

    def test_sans_etat_final_est_valide(self):
        AFND({"0", "1"}, {"a"}, "0", set(), {"0": {"a": {"1"}}})

    def test_tous_les_etats_finaux_est_valide(self):
        AFND({"0", "1"}, {"a"}, "0", {"0", "1"}, {})

    def test_etat_initial_peut_etre_final(self):
        AFND({"0"}, {"a"}, "0", {"0"}, {})

    def test_epsilon_transition_valide_sans_etre_dans_l_alphabet(self):
        AFND({"0", "1"}, {"a"}, "0", {"1"}, {"0": {EPSILON: {"1"}}})

    def test_non_determinisme_valide(self):
        AFND({"0", "1", "2"}, {"a"}, "0", {"2"}, {"0": {"a": {"1", "2"}}})

    def test_etats_vides(self):
        with self.assertRaisesRegex(ValueError, "états est vide"):
            AFND(set(), {"a"}, "0", set(), {})

    def test_alphabet_vide(self):
        with self.assertRaisesRegex(ValueError, "alphabet est vide"):
            AFND({"0"}, set(), "0", set(), {})

    def test_symbole_de_deux_caracteres(self):
        with self.assertRaisesRegex(ValueError, "un seul caractère"):
            AFND({"0"}, {"ab"}, "0", set(), {})

    def test_symbole_vide(self):
        with self.assertRaises(ValueError):
            AFND({"0"}, {""}, "0", set(), {})

    def test_epsilon_interdit_dans_l_alphabet(self):
        with self.assertRaisesRegex(ValueError, "ε"):
            AFND({"0"}, {"a", EPSILON}, "0", set(), {})

    def test_etat_initial_inconnu(self):
        with self.assertRaisesRegex(ValueError, "initial"):
            AFND({"0"}, {"a"}, "9", set(), {})

    def test_etat_initial_vide(self):
        with self.assertRaisesRegex(ValueError, "initial"):
            AFND({"0"}, {"a"}, "", set(), {})

    def test_etat_final_inconnu(self):
        with self.assertRaisesRegex(ValueError, "final"):
            AFND({"0"}, {"a"}, "0", {"9"}, {})

    def test_un_etat_final_inconnu_parmi_des_valides(self):
        with self.assertRaisesRegex(ValueError, "final"):
            AFND({"0", "1"}, {"a"}, "0", {"1", "9"}, {})

    def test_transition_depuis_etat_inconnu(self):
        with self.assertRaisesRegex(ValueError, "inconnu"):
            AFND({"0"}, {"a"}, "0", set(), {"9": {"a": {"0"}}})

    def test_symbole_hors_alphabet(self):
        with self.assertRaisesRegex(ValueError, "alphabet"):
            AFND({"0", "1"}, {"a"}, "0", set(), {"0": {"b": {"1"}}})

    def test_destination_inconnue(self):
        with self.assertRaisesRegex(ValueError, "destination"):
            AFND({"0", "1"}, {"a"}, "0", set(), {"0": {"a": {"9"}}})

    def test_une_destination_inconnue_parmi_des_valides(self):
        with self.assertRaisesRegex(ValueError, "destination"):
            AFND({"0", "1"}, {"a"}, "0", set(), {"0": {"a": {"1", "9"}}})

    def test_destination_inconnue_pour_epsilon(self):
        with self.assertRaisesRegex(ValueError, "destination"):
            AFND({"0"}, {"a"}, "0", set(), {"0": {EPSILON: {"9"}}})

    def test_les_messages_citent_le_nom_fautif(self):
        with self.assertRaisesRegex(ValueError, "zzz"):
            AFND({"0"}, {"a"}, "zzz", set(), {})


class TestDestinations(unittest.TestCase):
    def setUp(self):
        self.afnd = AFND(
            {"0", "1", "2"}, {"a", "b"}, "0", {"2"},
            {"0": {"a": {"1", "2"}, EPSILON: {"1"}}, "1": {"b": {"2"}}},
        )

    def test_destinations_existantes(self):
        self.assertEqual(self.afnd.destinations("0", "a"), {"1", "2"})

    def test_une_seule_destination(self):
        self.assertEqual(self.afnd.destinations("1", "b"), {"2"})

    def test_destinations_epsilon(self):
        self.assertEqual(self.afnd.destinations("0", EPSILON), {"1"})

    def test_symbole_sans_transition(self):
        self.assertEqual(self.afnd.destinations("0", "b"), set())

    def test_etat_sans_aucune_transition(self):
        self.assertEqual(self.afnd.destinations("2", "a"), set())

    def test_etat_inconnu(self):
        self.assertEqual(self.afnd.destinations("zzz", "a"), set())

    def test_symbole_inconnu(self):
        self.assertEqual(self.afnd.destinations("0", "z"), set())


class TestCreerAFND(unittest.TestCase):
    def test_exemple_simple(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        self.assertEqual(afnd.etats, {"0", "1"})
        self.assertEqual(afnd.alphabet, {"a", "b"})
        self.assertEqual(afnd.etat_initial, "0")
        self.assertEqual(afnd.etats_finaux, {"1"})
        self.assertEqual(afnd.transitions, {"0": {"a": {"1"}}})

    def test_etat_initial_avec_espaces_autour(self):
        afnd = creer_afnd("0, 1", "a", "  0  ", "1", "")
        self.assertEqual(afnd.etat_initial, "0")

    def test_plusieurs_etats_finaux(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "1, 2", "")
        self.assertEqual(afnd.etats_finaux, {"1", "2"})

    def test_aucun_etat_final(self):
        afnd = creer_afnd("0", "a", "0", "", "")
        self.assertEqual(afnd.etats_finaux, set())

    def test_doublons_dans_les_etats_disparaissent(self):
        afnd = creer_afnd("0, 0, 1", "a, a", "0", "1, 1", "")
        self.assertEqual(afnd.etats, {"0", "1"})
        self.assertEqual(afnd.alphabet, {"a"})
        self.assertEqual(afnd.etats_finaux, {"1"})

    def test_epsilon_transitions(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 eps 1")
        self.assertEqual(afnd.destinations("0", EPSILON), {"1"})

    def test_alphabet_sans_separateur_est_refuse(self):
        with self.assertRaisesRegex(ValueError, "un seul caractère"):
            creer_afnd("0", "ab", "0", "", "")

    def test_etat_initial_vide_est_refuse(self):
        with self.assertRaises(ValueError):
            creer_afnd("0", "a", "", "", "")

    def test_etat_initial_inconnu_est_refuse(self):
        with self.assertRaises(ValueError):
            creer_afnd("0", "a", "7", "", "")

    def test_etat_final_inconnu_est_refuse(self):
        with self.assertRaises(ValueError):
            creer_afnd("0", "a", "0", "7", "")

    def test_transition_mal_ecrite_est_refusee(self):
        with self.assertRaisesRegex(ValueError, "Ligne 1"):
            creer_afnd("0, 1", "a", "0", "1", "0 a")

    def test_transition_vers_etat_inconnu_est_refusee(self):
        with self.assertRaises(ValueError):
            creer_afnd("0", "a", "0", "", "0 a 5")

    def test_transition_avec_symbole_inconnu_est_refusee(self):
        with self.assertRaises(ValueError):
            creer_afnd("0, 1", "a", "0", "", "0 z 1")

    def test_etats_vides_refuses(self):
        with self.assertRaises(ValueError):
            creer_afnd("", "a", "0", "", "")

    def test_alphabet_vide_refuse(self):
        with self.assertRaises(ValueError):
            creer_afnd("0", "", "0", "", "")

    def test_epsilon_dans_l_alphabet_refuse(self):
        with self.assertRaises(ValueError):
            creer_afnd("0", "a, ε", "0", "", "")


if __name__ == "__main__":
    unittest.main()
