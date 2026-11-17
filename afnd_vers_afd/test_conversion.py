"""Tests unitaires de conversion.py : ε-fermeture, Transiter, et l'algorithme des sous-ensembles."""

import copy
import random
import unittest
from itertools import product

from afnd import AFND, EPSILON, creer_afnd
from conversion import (
    construire_afd,
    epsilon_fermeture,
    nom_etat,
    table_afd,
    texte_ensemble,
    transiter,
    trier,
)
from exemple import afnd_cours


# ----------------------------------------------------------------------
# Outils pour les tests
# ----------------------------------------------------------------------

def afnd_accepte(afnd, mot):
    """Simulation directe de l'AFND (sans utiliser conversion.py) : on explore tous les chemins.

    On part de (état initial, position 0) et on avance soit avec une ε-transition,
    soit en lisant le caractère suivant. Le mot est accepté si on arrive sur un état
    final après avoir lu tout le mot.
    """
    a_visiter = [(afnd.etat_initial, 0)]
    deja_vus = set()

    while len(a_visiter) > 0:
        etat, position = a_visiter.pop()
        if (etat, position) in deja_vus:
            continue
        deja_vus.add((etat, position))

        if position == len(mot) and etat in afnd.etats_finaux:
            return True

        for suivant in afnd.destinations(etat, EPSILON):
            a_visiter.append((suivant, position))
        if position < len(mot):
            for suivant in afnd.destinations(etat, mot[position]):
                a_visiter.append((suivant, position + 1))

    return False


def afnd_aleatoire(hasard, symboles=("a", "b"), avec_epsilon=True):
    """Fabrique un AFND au hasard (3 à 6 états)."""
    nombre = hasard.randint(3, 6)
    etats = {str(i) for i in range(nombre)}
    choix = list(symboles)
    if avec_epsilon:
        choix.append(EPSILON)
    transitions = {}

    for _ in range(hasard.randint(3, 14)):
        etat = str(hasard.randrange(nombre))
        symbole = hasard.choice(choix)
        destination = str(hasard.randrange(nombre))
        if etat not in transitions:
            transitions[etat] = {}
        if symbole not in transitions[etat]:
            transitions[etat][symbole] = set()
        transitions[etat][symbole].add(destination)

    finaux = {etat for etat in etats if hasard.random() < 0.4}
    return AFND(etats, set(symboles), "0", finaux, transitions)


def tous_les_mots(alphabet, longueur_max):
    mots = []
    for longueur in range(0, longueur_max + 1):
        for lettres in product(alphabet, repeat=longueur):
            mots.append("".join(lettres))
    return mots


def etats_accessibles(afd):
    """Les états de l'AFD qu'on peut atteindre depuis l'état initial."""
    vus = {afd.etat_initial}
    a_visiter = [afd.etat_initial]
    while len(a_visiter) > 0:
        etat = a_visiter.pop()
        for symbole in afd.alphabet:
            suivant = afd.transitions[etat][symbole]
            if suivant not in vus:
                vus.add(suivant)
                a_visiter.append(suivant)
    return vus


def afnd_n_ieme_lettre_avant_la_fin(n):
    """Mots sur {a, b} dont la n-ième lettre avant la fin est « a ».

    L'AFND a n+1 états, mais l'AFD minimal a 2^n états : c'est le cas classique
    où la construction des sous-ensembles « explose ».
    """
    lignes = ["0 a 0", "0 b 0", "0 a 1"]
    for i in range(1, n):
        lignes.append(f"{i} a {i + 1}")
        lignes.append(f"{i} b {i + 1}")
    etats = ", ".join(str(i) for i in range(n + 1))
    return creer_afnd(etats, "a, b", "0", str(n), "\n".join(lignes))


# ----------------------------------------------------------------------
# trier, texte_ensemble, nom_etat
# ----------------------------------------------------------------------

class TestTrier(unittest.TestCase):
    def test_chiffres_dans_l_ordre_numerique(self):
        self.assertEqual(trier({"10", "2", "1", "9"}), ["1", "2", "9", "10"])

    def test_2_avant_10(self):
        self.assertEqual(trier({"10", "2"}), ["2", "10"])

    def test_ensemble_vide(self):
        self.assertEqual(trier(set()), [])

    def test_noms_avec_lettres(self):
        self.assertEqual(trier({"q2", "q0", "q1"}), ["q0", "q1", "q2"])

    def test_noms_avec_lettres_et_nombres_a_plusieurs_chiffres(self):
        self.assertEqual(trier({"q10", "q9", "q1"}), ["q1", "q9", "q10"])

    def test_un_seul_element(self):
        self.assertEqual(trier({"x"}), ["x"])

    def test_retourne_une_liste(self):
        self.assertIsInstance(trier({"1"}), list)

    def test_accepte_un_frozenset(self):
        self.assertEqual(trier(frozenset({"3", "1"})), ["1", "3"])


class TestTexteEnsemble(unittest.TestCase):
    def test_ensemble_vide(self):
        self.assertEqual(texte_ensemble(set()), "∅")

    def test_frozenset_vide(self):
        self.assertEqual(texte_ensemble(frozenset()), "∅")

    def test_un_element(self):
        self.assertEqual(texte_ensemble({"0"}), "{0}")

    def test_plusieurs_elements_tries(self):
        self.assertEqual(texte_ensemble({"2", "0", "1"}), "{0, 1, 2}")

    def test_tri_naturel(self):
        self.assertEqual(texte_ensemble({"10", "9", "1"}), "{1, 9, 10}")

    def test_cours_etat_a(self):
        self.assertEqual(texte_ensemble({"0", "1", "2", "4", "7"}), "{0, 1, 2, 4, 7}")

    def test_noms_de_plusieurs_caracteres(self):
        self.assertEqual(texte_ensemble({"q1", "q0"}), "{q0, q1}")


class TestNomEtat(unittest.TestCase):
    def test_premiers_noms(self):
        self.assertEqual([nom_etat(i) for i in range(5)], ["A", "B", "C", "D", "E"])

    def test_vingt_six_lettres(self):
        self.assertEqual(nom_etat(0), "A")
        self.assertEqual(nom_etat(25), "Z")

    def test_apres_z(self):
        self.assertEqual(nom_etat(26), "S26")
        self.assertEqual(nom_etat(100), "S100")

    def test_tous_les_noms_sont_differents(self):
        noms = [nom_etat(i) for i in range(200)]
        self.assertEqual(len(set(noms)), 200)


# ----------------------------------------------------------------------
# epsilon_fermeture
# ----------------------------------------------------------------------

class TestEpsilonFermeture(unittest.TestCase):
    def test_ensemble_vide(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, set()), set())

    def test_etat_sans_epsilon_transition_reste_seul(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, {"2"}), {"2"})

    def test_l_etat_lui_meme_fait_partie_de_la_fermeture(self):
        self.assertIn("5", epsilon_fermeture(afnd_cours, {"5"}))

    def test_une_epsilon_transition(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 eps 1")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0", "1"})

    def test_la_fermeture_n_est_pas_symetrique(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 eps 1")
        self.assertEqual(epsilon_fermeture(afnd, {"1"}), {"1"})

    def test_chaine_d_epsilon_transitions(self):
        afnd = creer_afnd("0, 1, 2, 3", "a", "0", "3", "0 eps 1\n1 eps 2\n2 eps 3")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0", "1", "2", "3"})

    def test_cycle_d_epsilon_transitions(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 eps 1\n1 eps 0")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0", "1"})
        self.assertEqual(epsilon_fermeture(afnd, {"1"}), {"0", "1"})

    def test_epsilon_boucle_sur_soi_meme(self):
        afnd = creer_afnd("0", "a", "0", "0", "0 eps 0")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0"})

    def test_les_transitions_normales_sont_ignorees(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 a 1")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0"})

    def test_melange_de_transitions_normales_et_epsilon(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 1\n0 eps 2")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0", "2"})

    def test_on_ne_traverse_pas_une_transition_normale(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 1\n1 eps 2")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0"})

    def test_plusieurs_epsilon_transitions_depuis_le_meme_etat(self):
        afnd = creer_afnd("0, 1, 2, 3", "a", "0", "3", "0 eps 1\n0 eps 2\n0 eps 3")
        self.assertEqual(epsilon_fermeture(afnd, {"0"}), {"0", "1", "2", "3"})

    def test_fermeture_d_un_ensemble_est_l_union_des_fermetures(self):
        afnd = creer_afnd("0, 1, 2, 3", "a", "0", "3", "0 eps 1\n2 eps 3")
        union = epsilon_fermeture(afnd, {"0"}) | epsilon_fermeture(afnd, {"2"})
        self.assertEqual(epsilon_fermeture(afnd, {"0", "2"}), union)

    def test_fermeture_contient_toujours_l_ensemble_de_depart(self):
        ensemble = {"3", "8", "5"}
        self.assertTrue(ensemble <= epsilon_fermeture(afnd_cours, ensemble))

    def test_fermeture_d_une_fermeture_ne_change_rien(self):
        premiere = epsilon_fermeture(afnd_cours, {"0"})
        self.assertEqual(epsilon_fermeture(afnd_cours, premiere), premiere)

    def test_ne_modifie_pas_l_ensemble_donne(self):
        ensemble = {"0"}
        epsilon_fermeture(afnd_cours, ensemble)
        self.assertEqual(ensemble, {"0"})

    def test_accepte_un_frozenset(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, frozenset({"2"})), {"2"})

    def test_cours_fermeture_de_0(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, {"0"}), {"0", "1", "2", "4", "7"})

    def test_cours_fermeture_de_1(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, {"1"}), {"1", "2", "4"})

    def test_cours_fermeture_de_3_et_8(self):
        self.assertEqual(
            epsilon_fermeture(afnd_cours, {"3", "8"}),
            {"1", "2", "3", "4", "6", "7", "8"},
        )

    def test_cours_fermeture_de_5(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, {"5"}), {"1", "2", "4", "5", "6", "7"})

    def test_cours_fermeture_de_5_et_9(self):
        self.assertEqual(
            epsilon_fermeture(afnd_cours, {"5", "9"}),
            {"1", "2", "4", "5", "6", "7", "9"},
        )

    def test_cours_fermeture_de_5_et_10(self):
        self.assertEqual(
            epsilon_fermeture(afnd_cours, {"5", "10"}),
            {"1", "2", "4", "5", "6", "7", "10"},
        )

    def test_cours_fermeture_de_6(self):
        self.assertEqual(epsilon_fermeture(afnd_cours, {"6"}), {"6", "1", "7", "2", "4"})


# ----------------------------------------------------------------------
# transiter
# ----------------------------------------------------------------------

class TestTransiter(unittest.TestCase):
    def test_une_transition(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 a 1")
        self.assertEqual(transiter(afnd, {"0"}, "a"), {"1"})

    def test_aucune_transition_donne_ensemble_vide(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        self.assertEqual(transiter(afnd, {"0"}, "b"), set())

    def test_ensemble_vide(self):
        self.assertEqual(transiter(afnd_cours, set(), "a"), set())

    def test_non_determinisme(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 1\n0 a 2")
        self.assertEqual(transiter(afnd, {"0"}, "a"), {"1", "2"})

    def test_union_sur_plusieurs_etats(self):
        afnd = creer_afnd("0, 1, 2, 3", "a", "0", "3", "0 a 2\n1 a 3")
        self.assertEqual(transiter(afnd, {"0", "1"}, "a"), {"2", "3"})

    def test_destinations_communes_comptees_une_fois(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 2\n1 a 2")
        self.assertEqual(transiter(afnd, {"0", "1"}, "a"), {"2"})

    def test_ne_suit_pas_les_epsilon_transitions(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 1\n1 eps 2")
        self.assertEqual(transiter(afnd, {"0"}, "a"), {"1"})

    def test_ignore_les_epsilon_transitions_de_depart(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 eps 1\n1 a 2")
        self.assertEqual(transiter(afnd, {"0"}, "a"), set())

    def test_etat_inconnu_donne_ensemble_vide(self):
        self.assertEqual(transiter(afnd_cours, {"zzz"}, "a"), set())

    def test_symbole_inconnu_donne_ensemble_vide(self):
        self.assertEqual(transiter(afnd_cours, {"2"}, "z"), set())

    def test_boucle(self):
        afnd = creer_afnd("0", "a", "0", "0", "0 a 0")
        self.assertEqual(transiter(afnd, {"0"}, "a"), {"0"})

    def test_ne_modifie_pas_l_ensemble_donne(self):
        ensemble = {"2", "7"}
        transiter(afnd_cours, ensemble, "a")
        self.assertEqual(ensemble, {"2", "7"})

    def test_ne_modifie_pas_l_automate(self):
        copie = copy.deepcopy(afnd_cours.transitions)
        transiter(afnd_cours, {"2", "7"}, "a")
        self.assertEqual(afnd_cours.transitions, copie)

    def test_resultat_independant_de_l_ordre(self):
        a = transiter(afnd_cours, {"2", "7", "4"}, "a")
        b = transiter(afnd_cours, {"4", "2", "7"}, "a")
        self.assertEqual(a, b)

    def test_cours_transiter_etat_a_sur_a(self):
        self.assertEqual(transiter(afnd_cours, {"0", "1", "2", "4", "7"}, "a"), {"3", "8"})

    def test_cours_transiter_etat_a_sur_b(self):
        self.assertEqual(transiter(afnd_cours, {"0", "1", "2", "4", "7"}, "b"), {"5"})

    def test_cours_transiter_etat_b_sur_b(self):
        self.assertEqual(transiter(afnd_cours, {"1", "2", "3", "4", "6", "7", "8"}, "b"), {"5", "9"})

    def test_cours_transiter_etat_d_sur_b(self):
        self.assertEqual(transiter(afnd_cours, {"1", "2", "4", "5", "6", "7", "9"}, "b"), {"5", "10"})


# ----------------------------------------------------------------------
# construire_afd : l'exemple du cours
# ----------------------------------------------------------------------

class TestConstruireAFDCours(unittest.TestCase):
    def setUp(self):
        self.afd, self.noms, self.etapes = construire_afd(afnd_cours)

    def test_afnd_du_cours_a_11_etats(self):
        self.assertEqual(len(afnd_cours.etats), 11)

    def test_afd_a_5_etats(self):
        self.assertEqual(self.afd.etats, {"A", "B", "C", "D", "E"})

    def test_alphabet_conserve(self):
        self.assertEqual(self.afd.alphabet, {"a", "b"})

    def test_etat_initial_est_a(self):
        self.assertEqual(self.afd.etat_initial, "A")

    def test_seul_etat_final_est_e(self):
        self.assertEqual(self.afd.etats_finaux, {"E"})

    def test_noms_et_ensembles(self):
        attendu = {
            frozenset({"0", "1", "2", "4", "7"}): "A",
            frozenset({"1", "2", "3", "4", "6", "7", "8"}): "B",
            frozenset({"1", "2", "4", "5", "6", "7"}): "C",
            frozenset({"1", "2", "4", "5", "6", "7", "9"}): "D",
            frozenset({"1", "2", "4", "5", "6", "7", "10"}): "E",
        }
        self.assertEqual(self.noms, attendu)

    def test_table_de_transitions_du_cours(self):
        attendu = {
            "A": {"a": "B", "b": "C"},
            "B": {"a": "B", "b": "D"},
            "C": {"a": "B", "b": "C"},
            "D": {"a": "B", "b": "E"},
            "E": {"a": "B", "b": "C"},
        }
        self.assertEqual(self.afd.transitions, attendu)

    def test_mots_qui_se_terminent_par_abb(self):
        for mot in tous_les_mots("ab", 8):
            accepte, chemin, invalides = self.afd.reconnaitre(mot)
            self.assertEqual(accepte, mot.endswith("abb"), f"mot '{mot}'")

    def test_chemin_de_abb(self):
        accepte, chemin, invalides = self.afd.reconnaitre("abb")
        self.assertEqual(chemin, ["A", "B", "D", "E"])

    def test_etapes_commencent_par_le_depart(self):
        self.assertTrue(self.etapes[0].startswith("Départ"))
        self.assertIn("{0, 1, 2, 4, 7}", self.etapes[0])

    def test_une_ligne_traitement_par_etat_de_l_afd(self):
        lignes = [ligne for ligne in self.etapes if ligne.startswith("Traitement")]
        self.assertEqual(len(lignes), 5)

    def test_une_ligne_par_etat_et_par_symbole(self):
        pour_a = [ligne for ligne in self.etapes if ligne.startswith("  Pour a")]
        pour_b = [ligne for ligne in self.etapes if ligne.startswith("  Pour b")]
        self.assertEqual(len(pour_a), 5)
        self.assertEqual(len(pour_b), 5)

    def test_premiere_etape_transiter_sur_a(self):
        self.assertIn("Transiter(T, a) = {3, 8}", self.etapes[3])
        self.assertIn("{1, 2, 3, 4, 6, 7, 8}", self.etapes[3])

    def test_la_conversion_ne_modifie_pas_l_afnd(self):
        avant = copy.deepcopy(afnd_cours.transitions)
        construire_afd(afnd_cours)
        self.assertEqual(afnd_cours.transitions, avant)
        self.assertEqual(len(afnd_cours.etats), 11)

    def test_deux_conversions_donnent_le_meme_resultat(self):
        afd2, noms2, etapes2 = construire_afd(afnd_cours)
        self.assertEqual(afd2.transitions, self.afd.transitions)
        self.assertEqual(noms2, self.noms)
        self.assertEqual(etapes2, self.etapes)


# ----------------------------------------------------------------------
# construire_afd : cas particuliers
# ----------------------------------------------------------------------

class TestConstruireAFDCasParticuliers(unittest.TestCase):
    def test_exemple_page_33_du_cours(self):
        # AFN M : q0 -a-> {q0, q1}, q0 -b-> q1, q1 -a,b-> q1, final q1
        afnd = creer_afnd("q0, q1", "a, b", "q0", "q1", "q0 a q0\nq0 a q1\nq0 b q1\nq1 a q1\nq1 b q1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(noms[frozenset({"q0"})], "A")
        self.assertEqual(noms[frozenset({"q0", "q1"})], "B")
        self.assertEqual(noms[frozenset({"q1"})], "C")
        self.assertEqual(afd.transitions, {
            "A": {"a": "B", "b": "C"},
            "B": {"a": "B", "b": "C"},
            "C": {"a": "C", "b": "C"},
        })
        self.assertEqual(afd.etats_finaux, {"B", "C"})

    def test_afnd_deja_deterministe_garde_le_meme_nombre_d_etats(self):
        afnd = creer_afnd("0, 1, 2", "a, b", "0", "2", "0 a 1\n0 b 0\n1 a 1\n1 b 2\n2 a 1\n2 b 0")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(len(afd.etats), 3)
        for ensemble in noms:
            self.assertEqual(len(ensemble), 1)

    def test_etat_puits_apparait_pour_une_transition_manquante(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertIn(frozenset(), noms)
        puits = noms[frozenset()]
        self.assertEqual(afd.transitions[puits], {"a": puits, "b": puits})

    def test_etat_puits_n_est_jamais_final(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertNotIn(noms[frozenset()], afd.etats_finaux)

    def test_noms_dans_l_ordre_de_decouverte_avec_puits(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(noms[frozenset({"0"})], "A")
        self.assertEqual(noms[frozenset({"1"})], "B")
        self.assertEqual(noms[frozenset()], "C")
        self.assertEqual(afd.etats_finaux, {"B"})

    def test_pas_de_puits_si_l_afnd_est_complet(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1\n0 b 0\n1 a 1\n1 b 0")
        afd, noms, etapes = construire_afd(afnd)
        self.assertNotIn(frozenset(), noms)

    def test_afnd_sans_aucune_transition(self):
        afnd = creer_afnd("0", "a", "0", "0", "")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(len(afd.etats), 2)  # {0} et le puits
        self.assertEqual(afd.etats_finaux, {"A"})

    def test_afnd_sans_aucune_transition_accepte_seulement_le_mot_vide(self):
        afnd = creer_afnd("0", "a", "0", "0", "")
        afd, noms, etapes = construire_afd(afnd)
        self.assertTrue(afd.reconnaitre("")[0])
        self.assertFalse(afd.reconnaitre("a")[0])
        self.assertFalse(afd.reconnaitre("aa")[0])

    def test_afnd_sans_etat_final_n_accepte_rien(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "", "0 a 1\n1 b 0\n0 eps 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(afd.etats_finaux, set())
        for mot in tous_les_mots("ab", 5):
            self.assertFalse(afd.reconnaitre(mot)[0])

    def test_etat_initial_final_accepte_le_mot_vide(self):
        afnd = creer_afnd("0, 1", "a", "0", "0", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertIn(afd.etat_initial, afd.etats_finaux)
        self.assertTrue(afd.reconnaitre("")[0])

    def test_etat_final_atteint_par_epsilon_depuis_l_initial(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 eps 1\n1 eps 2")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(noms[frozenset({"0", "1", "2"})], "A")
        self.assertIn("A", afd.etats_finaux)
        self.assertTrue(afd.reconnaitre("")[0])

    def test_etat_initial_de_l_afd_est_la_fermeture_de_l_initial(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 eps 1")
        afd, noms, etapes = construire_afd(afnd)
        ensemble_initial = [ens for ens, nom in noms.items() if nom == afd.etat_initial][0]
        self.assertEqual(ensemble_initial, frozenset({"0", "1"}))

    def test_cycle_d_epsilon_transitions(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 eps 1\n1 eps 0\n1 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(len(afd.etats), 1)
        self.assertTrue(afd.reconnaitre("")[0])
        self.assertTrue(afd.reconnaitre("aaa")[0])

    def test_les_etats_inaccessibles_de_l_afnd_sont_ignores(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "1", "0 a 1\n2 a 2")
        afd, noms, etapes = construire_afd(afnd)
        for ensemble in noms:
            self.assertNotIn("2", ensemble)

    def test_un_seul_etat_avec_boucle(self):
        afnd = creer_afnd("0", "a, b", "0", "0", "0 a 0\n0 b 0")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(afd.etats, {"A"})
        self.assertEqual(afd.transitions, {"A": {"a": "A", "b": "A"}})

    def test_alphabet_d_un_seul_symbole(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 a 1\n1 a 0")
        afd, noms, etapes = construire_afd(afnd)
        for n in range(0, 8):
            self.assertEqual(afd.reconnaitre("a" * n)[0], n % 2 == 1)

    def test_alphabet_de_trois_symboles(self):
        afnd = creer_afnd("0, 1", "a, b, c", "0", "1", "0 c 1\n0 a 0\n0 b 0")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(afd.alphabet, {"a", "b", "c"})
        for mot in tous_les_mots("abc", 4):
            self.assertEqual(afd.reconnaitre(mot)[0], afnd_accepte(afnd, mot), f"mot '{mot}'")

    def test_symbole_de_l_alphabet_jamais_utilise(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertEqual(afd.alphabet, {"a", "b"})
        self.assertFalse(afd.reconnaitre("b")[0])

    def test_non_determinisme_simple(self):
        # 0 -a-> 1 et 0 -a-> 2, seul 2 est final, 2 -b-> 2
        afnd = creer_afnd("0, 1, 2", "a, b", "0", "2", "0 a 1\n0 a 2\n2 b 2")
        afd, noms, etapes = construire_afd(afnd)
        self.assertTrue(afd.reconnaitre("a")[0])
        self.assertTrue(afd.reconnaitre("abbb")[0])
        self.assertFalse(afd.reconnaitre("b")[0])
        self.assertFalse(afd.reconnaitre("ab" + "a")[0])

    def test_le_choix_non_deterministe_est_exploite(self):
        # Le mot « ab » n'est accepté que par la branche 0 -a-> 2 -b-> 3.
        afnd = creer_afnd("0, 1, 2, 3", "a, b", "0", "3", "0 a 1\n0 a 2\n2 b 3")
        afd, noms, etapes = construire_afd(afnd)
        self.assertTrue(afd.reconnaitre("ab")[0])

    def test_les_deux_ensembles_ont_le_meme_nombre_d_etats_que_les_noms(self):
        afd, noms, etapes = construire_afd(afnd_cours)
        self.assertEqual(len(noms), len(afd.etats))

    def test_plusieurs_etats_finaux_dans_l_afnd(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "1, 2", "0 a 1\n1 a 2")
        afd, noms, etapes = construire_afd(afnd)
        self.assertFalse(afd.reconnaitre("")[0])
        self.assertTrue(afd.reconnaitre("a")[0])
        self.assertTrue(afd.reconnaitre("aa")[0])
        self.assertFalse(afd.reconnaitre("aaa")[0])


# ----------------------------------------------------------------------
# construire_afd : l'explosion du nombre d'états (2^n)
# ----------------------------------------------------------------------

class TestExplosion(unittest.TestCase):
    def test_n_egal_1_donne_2_etats(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(1))
        self.assertEqual(len(afd.etats), 2)

    def test_n_egal_2_donne_4_etats(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(2))
        self.assertEqual(len(afd.etats), 4)

    def test_n_egal_3_donne_8_etats(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(3))
        self.assertEqual(len(afd.etats), 8)

    def test_n_egal_4_donne_16_etats(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(4))
        self.assertEqual(len(afd.etats), 16)

    def test_n_egal_5_donne_32_etats_et_les_noms_depassent_z(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(5))
        self.assertEqual(len(afd.etats), 32)
        self.assertIn("Z", afd.etats)
        self.assertIn("S26", afd.etats)
        self.assertIn("S31", afd.etats)

    def test_n_egal_3_reconnait_la_bonne_langue(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(3))
        for mot in tous_les_mots("ab", 8):
            attendu = len(mot) >= 3 and mot[-3] == "a"
            self.assertEqual(afd.reconnaitre(mot)[0], attendu, f"mot '{mot}'")

    def test_n_egal_5_reconnait_la_bonne_langue(self):
        afd, noms, etapes = construire_afd(afnd_n_ieme_lettre_avant_la_fin(5))
        for mot in tous_les_mots("ab", 8):
            attendu = len(mot) >= 5 and mot[-5] == "a"
            self.assertEqual(afd.reconnaitre(mot)[0], attendu, f"mot '{mot}'")


# ----------------------------------------------------------------------
# Propriétés vraies pour n'importe quel AFND (AFND aléatoires)
# ----------------------------------------------------------------------

class TestProprietesAleatoires(unittest.TestCase):
    NOMBRE = 150

    def afnd_et_afd(self, graine, symboles=("a", "b"), avec_epsilon=True):
        """Génère NOMBRE AFND avec leur AFD."""
        hasard = random.Random(graine)
        for _ in range(self.NOMBRE):
            afnd = afnd_aleatoire(hasard, symboles, avec_epsilon)
            afd, noms, etapes = construire_afd(afnd)
            yield afnd, afd, noms, etapes

    def test_meme_langage_avec_epsilon_transitions(self):
        mots = tous_les_mots("ab", 6)
        for afnd, afd, noms, etapes in self.afnd_et_afd(2024):
            for mot in mots:
                self.assertEqual(afd.reconnaitre(mot)[0], afnd_accepte(afnd, mot), f"mot '{mot}'")

    def test_meme_langage_sans_epsilon_transitions(self):
        mots = tous_les_mots("ab", 6)
        for afnd, afd, noms, etapes in self.afnd_et_afd(7, avec_epsilon=False):
            for mot in mots:
                self.assertEqual(afd.reconnaitre(mot)[0], afnd_accepte(afnd, mot), f"mot '{mot}'")

    def test_meme_langage_avec_trois_symboles(self):
        mots = tous_les_mots("abc", 4)
        for afnd, afd, noms, etapes in self.afnd_et_afd(99, symboles=("a", "b", "c")):
            for mot in mots:
                self.assertEqual(afd.reconnaitre(mot)[0], afnd_accepte(afnd, mot), f"mot '{mot}'")

    def test_meme_langage_avec_un_seul_symbole(self):
        mots = tous_les_mots("a", 8)
        for afnd, afd, noms, etapes in self.afnd_et_afd(5, symboles=("a",)):
            for mot in mots:
                self.assertEqual(afd.reconnaitre(mot)[0], afnd_accepte(afnd, mot), f"mot '{mot}'")

    def test_l_afd_est_complet_et_deterministe(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(11):
            for etat in afd.etats:
                self.assertEqual(set(afd.transitions[etat]), afd.alphabet)
                for symbole in afd.alphabet:
                    self.assertIn(afd.transitions[etat][symbole], afd.etats)

    def test_tous_les_etats_de_l_afd_sont_accessibles(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(12):
            self.assertEqual(etats_accessibles(afd), afd.etats)

    def test_les_noms_sont_uniques_et_correspondent_aux_etats(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(13):
            self.assertEqual(len(set(noms.values())), len(noms))
            self.assertEqual(set(noms.values()), afd.etats)

    def test_un_etat_est_final_si_et_seulement_si_il_contient_un_etat_final(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(14):
            for ensemble, nom in noms.items():
                contient_un_final = len(ensemble & afnd.etats_finaux) > 0
                self.assertEqual(nom in afd.etats_finaux, contient_un_final)

    def test_les_ensembles_sont_des_ensembles_d_etats_de_l_afnd(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(15):
            for ensemble in noms:
                self.assertTrue(ensemble <= afnd.etats)

    def test_les_ensembles_sont_tous_differents(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(16):
            self.assertEqual(len(set(noms.keys())), len(noms))

    def test_chaque_ensemble_est_ferme_par_epsilon(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(17):
            for ensemble in noms:
                self.assertEqual(epsilon_fermeture(afnd, ensemble), set(ensemble))

    def test_transitions_conformes_a_la_definition(self):
        # delta_AFD(T, x) = ε-fermeture(Transiter(T, x))
        for afnd, afd, noms, etapes in self.afnd_et_afd(18):
            nom_vers_ensemble = {nom: ensemble for ensemble, nom in noms.items()}
            for nom, ensemble in nom_vers_ensemble.items():
                for symbole in afd.alphabet:
                    attendu = epsilon_fermeture(afnd, transiter(afnd, ensemble, symbole))
                    obtenu = nom_vers_ensemble[afd.transitions[nom][symbole]]
                    self.assertEqual(set(obtenu), attendu)

    def test_le_nombre_d_etats_est_au_plus_2_puissance_n(self):
        for afnd, afd, noms, etapes in self.afnd_et_afd(19):
            self.assertLessEqual(len(afd.etats), 2 ** len(afnd.etats))

    def test_la_conversion_ne_modifie_pas_l_afnd(self):
        hasard = random.Random(20)
        for _ in range(self.NOMBRE):
            afnd = afnd_aleatoire(hasard)
            avant = (set(afnd.etats), set(afnd.alphabet), afnd.etat_initial,
                     set(afnd.etats_finaux), copy.deepcopy(afnd.transitions))
            construire_afd(afnd)
            apres = (afnd.etats, afnd.alphabet, afnd.etat_initial, afnd.etats_finaux, afnd.transitions)
            self.assertEqual(avant, apres)

    def test_convertir_un_afd_deja_complet_donne_un_afd_equivalent(self):
        # Reconvertir l'AFD obtenu (vu comme un AFND) ne doit pas changer le langage.
        mots = tous_les_mots("ab", 6)
        hasard = random.Random(21)
        for _ in range(60):
            afnd = afnd_aleatoire(hasard)
            afd, noms, etapes = construire_afd(afnd)
            transitions = {etat: {x: {afd.transitions[etat][x]} for x in afd.alphabet} for etat in afd.etats}
            afnd2 = AFND(afd.etats, afd.alphabet, afd.etat_initial, afd.etats_finaux, transitions)
            afd2, noms2, etapes2 = construire_afd(afnd2)
            self.assertEqual(len(afd2.etats), len(afd.etats))
            for mot in mots:
                self.assertEqual(afd2.reconnaitre(mot)[0], afd.reconnaitre(mot)[0])


# ----------------------------------------------------------------------
# table_afd
# ----------------------------------------------------------------------

class TestTableAFD(unittest.TestCase):
    def setUp(self):
        self.afd, self.noms, self.etapes = construire_afd(afnd_cours)
        self.table = table_afd(self.afd, self.noms)
        self.lignes = self.table.splitlines()

    def test_contient_une_ligne_par_etat(self):
        for nom in ["A", "B", "C", "D", "E"]:
            lignes_de_l_etat = [ligne for ligne in self.lignes if ligne[4:10].strip() == nom]
            self.assertEqual(len(lignes_de_l_etat), 1, f"état {nom}")

    def test_l_entete_cite_les_symboles(self):
        entete = self.lignes[0]
        self.assertIn("a", entete)
        self.assertIn("b", entete)
        self.assertIn("État", entete)

    def test_marque_l_etat_initial(self):
        ligne_a = [ligne for ligne in self.lignes if ligne[4:10].strip() == "A"][0]
        self.assertTrue(ligne_a.startswith("->"))

    def test_marque_l_etat_final(self):
        ligne_e = [ligne for ligne in self.lignes if ligne[4:10].strip() == "E"][0]
        self.assertTrue(ligne_e.startswith("*"))

    def test_les_autres_etats_ne_sont_pas_marques(self):
        for nom in ["B", "C", "D"]:
            ligne = [ligne for ligne in self.lignes if ligne[4:10].strip() == nom][0]
            self.assertEqual(ligne[:4].strip(), "")

    def test_affiche_les_ensembles_de_l_afnd(self):
        self.assertIn("{0, 1, 2, 4, 7}", self.table)
        self.assertIn("{1, 2, 3, 4, 6, 7, 8}", self.table)
        self.assertIn("{1, 2, 4, 5, 6, 7, 10}", self.table)

    def test_ligne_de_l_etat_a(self):
        ligne_a = [ligne for ligne in self.lignes if ligne[4:10].strip() == "A"][0]
        self.assertEqual(ligne_a.split()[-2:], ["B", "C"])

    def test_ligne_de_l_etat_d(self):
        ligne_d = [ligne for ligne in self.lignes if ligne[4:10].strip() == "D"][0]
        self.assertEqual(ligne_d.split()[-2:], ["B", "E"])

    def test_etats_dans_l_ordre_alphabetique(self):
        noms_affiches = [ligne[4:10].strip() for ligne in self.lignes[2:7]]
        self.assertEqual(noms_affiches, ["A", "B", "C", "D", "E"])

    def test_contient_la_legende(self):
        self.assertIn("état initial", self.table)
        self.assertIn("état final", self.table)

    def test_l_ensemble_vide_s_affiche_avec_le_symbole_vide(self):
        afnd = creer_afnd("0, 1", "a, b", "0", "1", "0 a 1")
        afd, noms, etapes = construire_afd(afnd)
        self.assertIn("∅", table_afd(afd, noms))

    def test_l_etat_initial_final_porte_les_deux_marques(self):
        afnd = creer_afnd("0", "a", "0", "0", "0 a 0")
        afd, noms, etapes = construire_afd(afnd)
        ligne = table_afd(afd, noms).splitlines()[2]
        self.assertTrue(ligne.startswith("->*"))

    def test_retourne_du_texte(self):
        self.assertIsInstance(self.table, str)


# ----------------------------------------------------------------------
# L'exemple du cours (exemple.py)
# ----------------------------------------------------------------------

class TestExemple(unittest.TestCase):
    def test_etats_de_l_afnd_du_cours(self):
        self.assertEqual(afnd_cours.etats, {str(i) for i in range(11)})

    def test_etat_initial_et_final(self):
        self.assertEqual(afnd_cours.etat_initial, "0")
        self.assertEqual(afnd_cours.etats_finaux, {"10"})

    def test_epsilon_transitions_de_la_fig_2(self):
        self.assertEqual(afnd_cours.destinations("0", EPSILON), {"1", "7"})
        self.assertEqual(afnd_cours.destinations("1", EPSILON), {"2", "4"})
        self.assertEqual(afnd_cours.destinations("3", EPSILON), {"6"})
        self.assertEqual(afnd_cours.destinations("5", EPSILON), {"6"})
        self.assertEqual(afnd_cours.destinations("6", EPSILON), {"1", "7"})

    def test_transitions_normales_de_la_fig_2(self):
        self.assertEqual(afnd_cours.destinations("2", "a"), {"3"})
        self.assertEqual(afnd_cours.destinations("4", "b"), {"5"})
        self.assertEqual(afnd_cours.destinations("7", "a"), {"8"})
        self.assertEqual(afnd_cours.destinations("8", "b"), {"9"})
        self.assertEqual(afnd_cours.destinations("9", "b"), {"10"})

    def test_afnd_cours_reconnait_les_mots_qui_se_terminent_par_abb(self):
        for mot in tous_les_mots("ab", 7):
            self.assertEqual(afnd_accepte(afnd_cours, mot), mot.endswith("abb"), f"mot '{mot}'")

    def test_l_outil_de_simulation_refuse_le_mot_vide_pour_le_cours(self):
        self.assertFalse(afnd_accepte(afnd_cours, ""))


class TestOutilSimulationAFND(unittest.TestCase):
    """On vérifie l'outil de test lui-même, car les autres tests s'appuient dessus."""

    def test_accepte_le_mot_vide_si_l_initial_est_final(self):
        afnd = creer_afnd("0", "a", "0", "0", "")
        self.assertTrue(afnd_accepte(afnd, ""))

    def test_suit_les_epsilon_transitions(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 eps 1")
        self.assertTrue(afnd_accepte(afnd, ""))

    def test_explore_toutes_les_branches(self):
        afnd = creer_afnd("0, 1, 2", "a", "0", "2", "0 a 1\n0 a 2")
        self.assertTrue(afnd_accepte(afnd, "a"))

    def test_refuse_si_le_mot_n_est_pas_entierement_lu(self):
        afnd = creer_afnd("0, 1", "a", "0", "1", "0 a 1")
        self.assertFalse(afnd_accepte(afnd, "aa"))

    def test_termine_avec_un_cycle_d_epsilon(self):
        afnd = creer_afnd("0, 1", "a", "0", "", "0 eps 1\n1 eps 0")
        self.assertFalse(afnd_accepte(afnd, "a"))


if __name__ == "__main__":
    unittest.main()
