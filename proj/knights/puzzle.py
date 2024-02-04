from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

basicA = And(
    Or(AKnight, AKnave),
    Implication(AKnight, Not(AKnave)),
    Implication(AKnave, Not(AKnight))
)
basicB = And(
    Or(BKnight, BKnave),
    Implication(BKnight, Not(BKnave)),
    Implication(BKnave, Not(BKnight))
)
basicC = And(
    Or(CKnight, CKnave),
    Implication(CKnight, Not(CKnave)),
    Implication(CKnave, Not(CKnight))
)

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    basicA,
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    basicA, basicB,
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
ASays2 = Or(And(AKnight, BKnight), And(AKnave, BKnave))
BSays2 = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
    basicA, basicB,
    Implication(AKnight, ASays2),
    Implication(AKnave, Not(ASays2)),
    Implication(BKnight, BSays2),
    Implication(BKnave, Not(BSays2))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
ASaysKnight = And(
    Implication(AKnight, AKnight),
    Implication(AKnave, Not(AKnight))
)
ASaysKnave = And(
    Implication(AKnight, AKnave),
    Implication(AKnave, Not(AKnave))
)
knowledge3 = And(
    basicA, basicB, basicC,
    Implication(BKnight, And(ASaysKnave, CKnave)),
    Implication(BKnave, And(ASaysKnight, Not(CKnave))),
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
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
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
