from itertools import product

from afd import AFD
from exemple import afd_exemple

afd_pair = AFD(
    {"q0", "q1"},
    {"a", "b"},
    "q0",
    {"q0"},
    {
        "q0": {"a": "q1", "b": "q0"},
        "q1": {"a": "q0", "b": "q1"},
    },
)


def comparer(description, obtenu, attendu):
    if obtenu == attendu:
        print(f"  OK     {description}")
        return True
    print(f"  ECHEC  {description} : obtenu {obtenu}, attendu {attendu}")
    return False


def tester_mots(afd, cas):
    """cas = liste de (mot, accepté attendu)."""
    resultats = []
    for mot, attendu in cas:
        accepte, chemin, invalides = afd.reconnaitre(mot)
        nom = f"'{mot}'" if mot != "" else "'' (mot vide)"
        resultats.append(comparer(f"mot {nom}", accepte, attendu))
    return resultats


def main():
    resultats = []

    print("Automate 1 (mots qui se terminent par ab) - chaînes acceptées :")
    resultats += tester_mots(afd_exemple, [("ab", True), ("aab", True), ("bab", True), ("abab", True)])

    print("Automate 1 - chaînes rejetées :")
    resultats += tester_mots(afd_exemple, [("a", False), ("b", False), ("ba", False), ("abb", False)])

    print("Automate 1 - chaîne vide (rejetée car q0 n'est pas final) :")
    resultats += tester_mots(afd_exemple, [("", False)])

    print("Automate 2 (nombre pair de a) - chaîne vide (acceptée car q0 est final) :")
    resultats += tester_mots(afd_pair, [("", True), ("aa", True), ("bab", False), ("abab", True)])

    print("Automate 1 - symboles invalides (rejeté + symboles signalés) :")
    for mot, invalides_attendus in [("abc", ["c"]), ("xyz", ["x", "y", "z"]), ("a b", [" "])]:
        accepte, chemin, invalides = afd_exemple.reconnaitre(mot)
        resultats.append(comparer(f"mot '{mot}' rejeté", accepte, False))
        resultats.append(comparer(f"mot '{mot}' symboles invalides", invalides, invalides_attendus))

    print("Automate 1 - tous les mots de longueur 0 à 6 (attendu : mot.endswith('ab')) :")
    mots_faux = 0
    for longueur in range(0, 7):
        for lettres in product("ab", repeat=longueur):
            mot = "".join(lettres)
            accepte, chemin, invalides = afd_exemple.reconnaitre(mot)
            if accepte != mot.endswith("ab"):
                mots_faux += 1
    resultats.append(comparer("nombre de mots mal reconnus", mots_faux, 0))

    print()
    if all(resultats):
        print(f"Tous les tests sont réussis ({len(resultats)}/{len(resultats)}).")
    else:
        print(f"Des tests ont échoué : {resultats.count(True)}/{len(resultats)} réussis.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
