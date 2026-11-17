"""Tests unitaires de afd.py : la classe AFD, la reconnaissance de mots et le chemin."""

import unittest
from itertools import product

from afd import AFD, formater_chemin


def afd_se_termine_par_ab():
    """Mots sur {a, b} qui se terminent par « ab » (l'exemple de la fiche projet)."""
    return AFD(
        {"q0", "q1", "q2"}, {"a", "b"}, "q0", {"q2"},
        {
            "q0": {"a": "q1", "b": "q0"},
            "q1": {"a": "q1", "b": "q2"},
            "q2": {"a": "q1", "b": "q0"},
        },
    )


def afd_nombre_pair_de_a():
    """Mots sur {a, b} avec un nombre pair de « a » (le mot vide est accepté)."""
    return AFD(
        {"p", "i"}, {"a", "b"}, "p", {"p"},
        {"p": {"a": "i", "b": "p"}, "i": {"a": "p", "b": "i"}},
    )


def afd_accepte_tout():
    return AFD({"s"}, {"a", "b"}, "s", {"s"}, {"s": {"a": "s", "b": "s"}})


def afd_refuse_tout():
    return AFD({"s"}, {"a", "b"}, "s", set(), {"s": {"a": "s", "b": "s"}})


def afd_un_seul_symbole():
    """Mots a^n avec n multiple de 3."""
    return AFD(
        {"0", "1", "2"}, {"a"}, "0", {"0"},
        {"0": {"a": "1"}, "1": {"a": "2"}, "2": {"a": "0"}},
    )


class TestAFDVerifier(unittest.TestCase):
    def test_afd_valide(self):
        afd_se_termine_par_ab()

    def test_attributs_enregistres(self):
        afd = afd_se_termine_par_ab()
        self.assertEqual(afd.etats, {"q0", "q1", "q2"})
        self.assertEqual(afd.alphabet, {"a", "b"})
        self.assertEqual(afd.etat_initial, "q0")
        self.assertEqual(afd.etats_finaux, {"q2"})
        self.assertEqual(afd.transitions["q1"]["b"], "q2")

    def test_afd_sans_etat_final_est_valide(self):
        afd_refuse_tout()

    def test_etat_initial_inconnu(self):
        with self.assertRaisesRegex(ValueError, "initial"):
            AFD({"s"}, {"a"}, "x", set(), {"s": {"a": "s"}})

    def test_etat_final_inconnu(self):
        with self.assertRaisesRegex(ValueError, "final"):
            AFD({"s"}, {"a"}, "s", {"x"}, {"s": {"a": "s"}})

    def test_transition_manquante_pour_un_symbole(self):
        with self.assertRaisesRegex(ValueError, "Transition manquante"):
            AFD({"s"}, {"a", "b"}, "s", set(), {"s": {"a": "s"}})

    def test_transition_manquante_pour_un_etat(self):
        with self.assertRaisesRegex(ValueError, "Transition manquante"):
            AFD({"s", "t"}, {"a"}, "s", set(), {"s": {"a": "t"}})

    def test_aucune_transition(self):
        with self.assertRaisesRegex(ValueError, "Transition manquante"):
            AFD({"s"}, {"a"}, "s", set(), {})

    def test_le_message_cite_l_etat_et_le_symbole(self):
        with self.assertRaisesRegex(ValueError, r"delta\(s, b\)"):
            AFD({"s"}, {"a", "b"}, "s", set(), {"s": {"a": "s"}})


class TestReconnaitreSeTermineParAB(unittest.TestCase):
    def setUp(self):
        self.afd = afd_se_termine_par_ab()

    def test_mots_acceptes(self):
        for mot in ["ab", "aab", "bab", "abab", "bbab", "aaaab", "babab", "ababab"]:
            with self.subTest(mot=mot):
                accepte, chemin, invalides = self.afd.reconnaitre(mot)
                self.assertTrue(accepte)
                self.assertEqual(invalides, [])

    def test_mots_rejetes(self):
        for mot in ["a", "b", "aa", "bb", "ba", "abb", "abba", "aba", "bbb", "baa"]:
            with self.subTest(mot=mot):
                accepte, chemin, invalides = self.afd.reconnaitre(mot)
                self.assertFalse(accepte)
                self.assertEqual(invalides, [])

    def test_mot_vide_rejete(self):
        accepte, chemin, invalides = self.afd.reconnaitre("")
        self.assertFalse(accepte)
        self.assertEqual(chemin, ["q0"])
        self.assertEqual(invalides, [])

    def test_chemin_de_ab(self):
        accepte, chemin, invalides = self.afd.reconnaitre("ab")
        self.assertEqual(chemin, ["q0", "q1", "q2"])

    def test_chemin_de_abab(self):
        accepte, chemin, invalides = self.afd.reconnaitre("abab")
        self.assertEqual(chemin, ["q0", "q1", "q2", "q1", "q2"])

    def test_chemin_de_bba(self):
        accepte, chemin, invalides = self.afd.reconnaitre("bba")
        self.assertEqual(chemin, ["q0", "q0", "q0", "q1"])

    def test_le_chemin_commence_par_l_etat_initial(self):
        for mot in ["", "a", "b", "abab"]:
            with self.subTest(mot=mot):
                accepte, chemin, invalides = self.afd.reconnaitre(mot)
                self.assertEqual(chemin[0], "q0")

    def test_le_chemin_a_une_longueur_de_mot_plus_un(self):
        for mot in ["", "a", "ab", "abab", "bbbbbb"]:
            with self.subTest(mot=mot):
                accepte, chemin, invalides = self.afd.reconnaitre(mot)
                self.assertEqual(len(chemin), len(mot) + 1)

    def test_accepte_si_et_seulement_si_le_dernier_etat_est_final(self):
        for longueur in range(0, 6):
            for lettres in product("ab", repeat=longueur):
                mot = "".join(lettres)
                with self.subTest(mot=mot):
                    accepte, chemin, invalides = self.afd.reconnaitre(mot)
                    self.assertEqual(accepte, chemin[-1] in self.afd.etats_finaux)

    def test_tous_les_mots_jusqu_a_8_lettres_comparent_avec_endswith(self):
        for longueur in range(0, 9):
            for lettres in product("ab", repeat=longueur):
                mot = "".join(lettres)
                accepte, chemin, invalides = self.afd.reconnaitre(mot)
                self.assertEqual(accepte, mot.endswith("ab"), f"mot '{mot}'")

    def test_mot_tres_long(self):
        mot = "ba" * 5000 + "ab"
        accepte, chemin, invalides = self.afd.reconnaitre(mot)
        self.assertTrue(accepte)
        self.assertEqual(len(chemin), len(mot) + 1)

    def test_deux_lectures_du_meme_mot_donnent_le_meme_resultat(self):
        self.assertEqual(self.afd.reconnaitre("abab"), self.afd.reconnaitre("abab"))

    def test_la_lecture_ne_modifie_pas_l_automate(self):
        avant = {etat: dict(lignes) for etat, lignes in self.afd.transitions.items()}
        self.afd.reconnaitre("abababab")
        self.assertEqual(self.afd.transitions, avant)


class TestReconnaitreSymbolesInvalides(unittest.TestCase):
    def setUp(self):
        self.afd = afd_se_termine_par_ab()

    def test_un_symbole_invalide(self):
        accepte, chemin, invalides = self.afd.reconnaitre("abc")
        self.assertFalse(accepte)
        self.assertEqual(invalides, ["c"])

    def test_pas_de_chemin_si_symbole_invalide(self):
        accepte, chemin, invalides = self.afd.reconnaitre("abc")
        self.assertEqual(chemin, [])

    def test_plusieurs_symboles_invalides_tries(self):
        accepte, chemin, invalides = self.afd.reconnaitre("zyx")
        self.assertEqual(invalides, ["x", "y", "z"])

    def test_symbole_invalide_repete_signale_une_fois(self):
        accepte, chemin, invalides = self.afd.reconnaitre("cccab")
        self.assertEqual(invalides, ["c"])

    def test_symbole_invalide_au_debut(self):
        accepte, chemin, invalides = self.afd.reconnaitre("cab")
        self.assertFalse(accepte)
        self.assertEqual(invalides, ["c"])

    def test_symbole_invalide_au_milieu(self):
        accepte, chemin, invalides = self.afd.reconnaitre("acb")
        self.assertFalse(accepte)

    def test_symbole_invalide_a_la_fin(self):
        accepte, chemin, invalides = self.afd.reconnaitre("abx")
        self.assertFalse(accepte)
        self.assertEqual(invalides, ["x"])

    def test_mot_valide_avec_un_prefixe_accepte_mais_un_symbole_invalide(self):
        # « ab » est accepté, mais « abc » ne doit pas l'être.
        self.assertTrue(self.afd.reconnaitre("ab")[0])
        self.assertFalse(self.afd.reconnaitre("abc")[0])

    def test_majuscule_differente_de_minuscule(self):
        accepte, chemin, invalides = self.afd.reconnaitre("AB")
        self.assertFalse(accepte)
        self.assertEqual(invalides, ["A", "B"])

    def test_espace_est_un_symbole_invalide(self):
        accepte, chemin, invalides = self.afd.reconnaitre("a b")
        self.assertFalse(accepte)
        self.assertEqual(invalides, [" "])

    def test_chiffre_invalide(self):
        accepte, chemin, invalides = self.afd.reconnaitre("a1b")
        self.assertEqual(invalides, ["1"])

    def test_symbole_accentue_invalide(self):
        accepte, chemin, invalides = self.afd.reconnaitre("é")
        self.assertEqual(invalides, ["é"])

    def test_epsilon_n_est_pas_un_symbole_de_mot(self):
        accepte, chemin, invalides = self.afd.reconnaitre("aε")
        self.assertEqual(invalides, ["ε"])


class TestAutresAutomates(unittest.TestCase):
    def test_nombre_pair_de_a_mots_acceptes(self):
        afd = afd_nombre_pair_de_a()
        for mot in ["", "aa", "b", "bb", "aab", "abab", "baab", "aaaa"]:
            with self.subTest(mot=mot):
                self.assertTrue(afd.reconnaitre(mot)[0])

    def test_nombre_pair_de_a_mots_rejetes(self):
        afd = afd_nombre_pair_de_a()
        for mot in ["a", "ab", "ba", "aaa", "bab", "abbbb"]:
            with self.subTest(mot=mot):
                self.assertFalse(afd.reconnaitre(mot)[0])

    def test_nombre_pair_de_a_mot_vide_accepte_car_etat_initial_final(self):
        accepte, chemin, invalides = afd_nombre_pair_de_a().reconnaitre("")
        self.assertTrue(accepte)
        self.assertEqual(chemin, ["p"])

    def test_nombre_pair_de_a_compare_avec_count(self):
        afd = afd_nombre_pair_de_a()
        for longueur in range(0, 8):
            for lettres in product("ab", repeat=longueur):
                mot = "".join(lettres)
                self.assertEqual(afd.reconnaitre(mot)[0], mot.count("a") % 2 == 0, f"mot '{mot}'")

    def test_afd_qui_accepte_tout(self):
        afd = afd_accepte_tout()
        for mot in ["", "a", "b", "abba", "bbbbbbb"]:
            with self.subTest(mot=mot):
                self.assertTrue(afd.reconnaitre(mot)[0])

    def test_afd_qui_refuse_tout(self):
        afd = afd_refuse_tout()
        for mot in ["", "a", "b", "abba", "bbbbbbb"]:
            with self.subTest(mot=mot):
                self.assertFalse(afd.reconnaitre(mot)[0])

    def test_afd_qui_accepte_tout_rejette_quand_meme_un_symbole_invalide(self):
        accepte, chemin, invalides = afd_accepte_tout().reconnaitre("abc")
        self.assertFalse(accepte)
        self.assertEqual(invalides, ["c"])

    def test_alphabet_d_un_seul_symbole(self):
        afd = afd_un_seul_symbole()
        for n in range(0, 13):
            with self.subTest(n=n):
                self.assertEqual(afd.reconnaitre("a" * n)[0], n % 3 == 0)

    def test_chemin_qui_tourne_en_rond(self):
        accepte, chemin, invalides = afd_un_seul_symbole().reconnaitre("aaaaaa")
        self.assertEqual(chemin, ["0", "1", "2", "0", "1", "2", "0"])

    def test_automate_a_un_seul_etat_chemin_constant(self):
        accepte, chemin, invalides = afd_accepte_tout().reconnaitre("abab")
        self.assertEqual(chemin, ["s", "s", "s", "s", "s"])

    def test_alphabet_de_trois_symboles(self):
        # Mots sur {a, b, c} dont la dernière lettre est « c ».
        transitions = {}
        for etat in ["x", "y"]:
            transitions[etat] = {"a": "x", "b": "x", "c": "y"}
        afd = AFD({"x", "y"}, {"a", "b", "c"}, "x", {"y"}, transitions)
        self.assertTrue(afd.reconnaitre("abc")[0])
        self.assertTrue(afd.reconnaitre("cc")[0])
        self.assertFalse(afd.reconnaitre("cb")[0])
        self.assertFalse(afd.reconnaitre("")[0])

    def test_deux_etats_finaux(self):
        # Mots qui contiennent au moins un « a » : f1 puis f2 sont finals.
        afd = AFD(
            {"n", "f1", "f2"}, {"a", "b"}, "n", {"f1", "f2"},
            {"n": {"a": "f1", "b": "n"}, "f1": {"a": "f2", "b": "f1"}, "f2": {"a": "f1", "b": "f2"}},
        )
        self.assertFalse(afd.reconnaitre("bbb")[0])
        self.assertTrue(afd.reconnaitre("bab")[0])
        self.assertTrue(afd.reconnaitre("aa")[0])


class TestFormaterChemin(unittest.TestCase):
    def test_mot_vide(self):
        texte = formater_chemin("", ["A"])
        self.assertIn("mot vide", texte)
        self.assertIn("A", texte)

    def test_une_transition(self):
        self.assertEqual(formater_chemin("a", ["A", "B"]), "A --a--> B")

    def test_deux_transitions(self):
        self.assertEqual(formater_chemin("ab", ["A", "B", "C"]), "A --a--> B\nB --b--> C")

    def test_une_ligne_par_symbole(self):
        texte = formater_chemin("abba", ["A", "B", "C", "D", "E"])
        self.assertEqual(len(texte.splitlines()), 4)

    def test_boucle(self):
        self.assertEqual(formater_chemin("aa", ["B", "B", "B"]), "B --a--> B\nB --a--> B")

    def test_le_texte_correspond_au_resultat_de_reconnaitre(self):
        afd = afd_se_termine_par_ab()
        accepte, chemin, invalides = afd.reconnaitre("ab")
        self.assertEqual(formater_chemin("ab", chemin), "q0 --a--> q1\nq1 --b--> q2")

    def test_pas_de_retour_ligne_a_la_fin(self):
        self.assertFalse(formater_chemin("ab", ["A", "B", "C"]).endswith("\n"))


if __name__ == "__main__":
    unittest.main()
