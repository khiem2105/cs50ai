from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

#Base knowledge
baseA = And(
    Or(AKnave,AKnight),
    Implication(AKnave,Not(AKnight)),
    Implication(AKnight,Not(AKnave))
)
baseB = And(
    Or(BKnave,BKnight),
    Implication(BKnave,Not(BKnight)),
    Implication(BKnight,Not(BKnave))
)
baseC = And(
    Or(CKnave,CKnight),
    Implication(CKnave,Not(CKnight)),
    Implication(CKnight,Not(CKnave))
)
# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Implication(AKnight,And(AKnight,AKnave)),
    Implication(AKnave,Not(And(AKnave,AKnight))),
    baseA
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Implication(AKnave,Not(And(AKnave,BKnave))),
    Implication(AKnight,And(AKnave,BKnave)),
    baseA,
    baseB
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Implication(AKnight,Or(And(AKnight,BKnight),And(AKnave,BKnave))),
    Implication(AKnave,Not(Or(And(AKnight,BKnight),And(AKnave,BKnave)))),
    Implication(BKnight,Or(And(AKnave,BKnight),And(AKnight,BKnave))),
    Implication(BKnave,Not(Or(And(AKnave,BKnight),And(AKnight,BKnave)))),
    baseA,
    baseB
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Implication(BKnight, And(Implication(AKnight,AKnave),Implication(AKnave,Not(AKnave)))),
    Implication(BKnave, Not(And(Implication(AKnight,AKnave),Implication(AKnave,Not(AKnave))))),
    Implication(BKnight,CKnave),
    Implication(BKnave, CKnight),
    Implication(CKnight,AKnight),
    Implication(CKnave,AKnave),
    baseA,baseB,baseC    
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"{puzzle}:{symbol}")


if __name__ == "__main__":
    main()
