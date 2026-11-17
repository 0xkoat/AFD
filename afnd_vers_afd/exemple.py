"""Exemple du cours : l'AFND de l'expression régulière (a|b)*abb (Fig. 2), converti en AFD (Fig. 4).

Lancer :  python exemple.py   (affiche la conversion et crée afnd.png et afd.png)
"""

from afnd import AFND
from conversion import construire_afd, table_afd
from visualisation import dessiner_afd, dessiner_afnd

# Les ε-transitions sont écrites avec le symbole "ε".
afnd_cours = AFND(
    {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"},
    {"a", "b"},
    "0",
    {"10"},
    {
        "0": {"ε": {"1", "7"}},
        "1": {"ε": {"2", "4"}},
        "2": {"a": {"3"}},
        "3": {"ε": {"6"}},
        "4": {"b": {"5"}},
        "5": {"ε": {"6"}},
        "6": {"ε": {"1", "7"}},
        "7": {"a": {"8"}},
        "8": {"b": {"9"}},
        "9": {"b": {"10"}},
    },
)


if __name__ == "__main__":
    afd, noms, etapes = construire_afd(afnd_cours)

    print("\n".join(etapes))
    print()
    print(table_afd(afd, noms))

    dessiner_afnd(afnd_cours).render("afnd", cleanup=True)
    dessiner_afd(afd).render("afd", cleanup=True)
    print()
    print("Test de mots avec l'AFD :")
    for mot in ["abb", "aabb", "ab", ""]:
        accepte, chemin, invalides = afd.reconnaitre(mot)
        if accepte:
            verdict = "accepté"
        else:
            verdict = "rejeté"
        print(f"  '{mot}' : {verdict}   chemin : {' -> '.join(chemin)}")

    print()
    print("Images créées : afnd.png et afd.png")
