from random import choice
import unittest

from bcls.boolean import (
    And,
    BooleanTerm,
    Not,
    Or,
    Var,
    generate_all_variable_mappings,
    minimal_dnf,
    minimal_cnf,
)


def wikipedia_example() -> BooleanTerm[str]:
    return Or(
        And(Not(Var("A")), Var("B"), Not(Var("C")), Not(Var("D"))),  # 0100
        And(Var("A"), Not(Var("B")), Not(Var("C")), Not(Var("D"))),  # 1000
        And(Var("A"), Not(Var("B")), Not(Var("C")), Var("D")),  # 1001
        And(Var("A"), Var("B"), Not(Var("C")), Not(Var("D"))),  # 1100
        And(Var("A"), Not(Var("B")), Var("C"), Var("D")),  # 1011
        And(Var("A"), Var("B"), Var("C"), Not(Var("D"))),  # 1110
        And(Var("A"), Var("B"), Var("C"), Var("D")),  # 1111
    )


def random_example() -> BooleanTerm[str]:
    return Or(
        And(Not(Var("x2")), Not(Var("x1")), Not(Var("x0"))),
        And(Not(Var("x2")), Not(Var("x1")), (Var("x0"))),
        And(Not(Var("x2")), (Var("x1")), (Var("x0"))),
        And((Var("x2")), Not(Var("x1")), Not(Var("x0"))),
        And((Var("x2")), (Var("x1")), Not(Var("x0"))),
        And((Var("x2")), (Var("x1")), (Var("x0"))),
    )


def generate_random_term(
    depth: int, max_width: int, variables: list[str], can_be_var: bool = False
) -> BooleanTerm[str]:
    negated = choice([True, False])
    if depth == 0:
        term: BooleanTerm[str] = Var(choice(variables))
        if negated:
            term = Not(term)
        return term

    constructor = choice([And, Or] + ([Var] if can_be_var else []))
    if constructor == Var:
        term = Var(choice(variables))
        if negated:
            term = Not(term)
        return term

    subterms = []
    num_of_subterms = 2 + choice(range(max_width - 1))

    for _ in range(num_of_subterms):
        subterms.append(generate_random_term(depth - 1, max_width, variables, True))

    term = constructor(*subterms)

    return term


def check_equiv(term_1: BooleanTerm[str], term_2: BooleanTerm[str]) -> bool:
    variables = term_1.variables

    variable_list = list(variables)

    mappings = generate_all_variable_mappings(len(variable_list))

    for mapping in mappings:
        if term_1.evaluate(mapping, variable_list) != term_2.evaluate(
            mapping, variable_list
        ):
            return False

    return True


class TestBoolean(unittest.TestCase):
    def test_wikipedia_cnf(self) -> None:
        term = wikipedia_example()
        self.assertTrue(check_equiv(minimal_cnf(term), term))

    def test_wikipedia_dnf(self) -> None:
        term = wikipedia_example()
        self.assertTrue(check_equiv(minimal_dnf(term), term))

    def test_pre_calc_random_cnf(self) -> None:
        term = random_example()
        self.assertTrue(check_equiv(minimal_cnf(term), term))

    def test_pre_calc_random_dnf(self) -> None:
        term = random_example()
        self.assertTrue(check_equiv(minimal_dnf(term), term))

    def test_random_dnf(self) -> None:
        term = generate_random_term(5, 5, ["a", "b", "c", "d", "e", "f"])
        self.assertTrue(check_equiv(minimal_dnf(term), term))

    def test_random_cnf(self) -> None:
        term = generate_random_term(5, 5, ["a", "b", "c", "d", "e", "f"])
        self.assertTrue(check_equiv(minimal_dnf(term), term))


if __name__ == "__main__":
    unittest.main()
