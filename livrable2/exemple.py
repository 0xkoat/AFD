from afd import AFD
from visualisation import dessiner

etats = {"q0", "q1", "q2"}
alphabet = {"a", "b"}
etat_initial = "q0"
etats_finaux = {"q2"}

transitions = {
    "q0": {"a": "q1", "b": "q0"},
    "q1": {"a": "q1", "b": "q2"},
    "q2": {"a": "q1", "b": "q0"},
}

afd_exemple = AFD(etats, alphabet, etat_initial, etats_finaux, transitions)


if __name__ == "__main__":
    print("États         :", sorted(afd_exemple.etats))
    print("Alphabet      :", sorted(afd_exemple.alphabet))
    print("État initial  :", afd_exemple.etat_initial)
    print("États finaux  :", sorted(afd_exemple.etats_finaux))
    print("Transitions   :")
    for etat in sorted(afd_exemple.etats):
        for symbole in sorted(afd_exemple.alphabet):
            print(f"  delta({etat}, {symbole}) = {afd_exemple.transitions[etat][symbole]}")

    dessiner(afd_exemple).render("afd_exemple", cleanup=True)
    print("Image créée : afd_exemple.png")
