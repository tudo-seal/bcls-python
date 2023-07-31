from collections.abc import Callable
import unittest
import logging

from bcls import (
    Type,
    Constructor,
    Arrow,
    Intersection,
    Var,
    FiniteCombinatoryLogic,
    enumerate_terms,
    Subtypes,
)
from bcls.enumeration import interpret_term


class TestExample1(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(module)s %(levelname)s: %(message)s",
        # level=logging.INFO,
    )

    def setUp(self) -> None:
        a: Type = Constructor("a")
        b: Type = Constructor("b")
        c: Type = Constructor("c")
        d: Type = Constructor("d")

        X: str = "X"
        Y: str = "Y"
        F: Callable[[str], str] = lambda x: f"F({x})"

        repository: dict[str | Callable[[str], str], Type] = dict(
            {
                X: Intersection(Intersection(a, b), d),
                Y: d,
                F: Intersection(Arrow(a, b), Arrow(d, Intersection(a, c))),
            }
        )
        environment: dict[str, set[str]] = dict()
        subtypes = Subtypes(environment)

        target = Var(a) & ~(Var(b) & Var(c))
        # target = Var(b)

        fcl = FiniteCombinatoryLogic(repository, subtypes)
        result = fcl.inhabit(target)

        self.enumerated_result = list(enumerate_terms(target, result))

        for real_result in self.enumerated_result:
            term = interpret_term(real_result)
            self.logger.info(term)

    def test_length(self) -> None:
        self.assertEqual(2, len(self.enumerated_result))

    def test_elements(self) -> None:
        self.assertEqual(
            ["X", "F(Y)"], [interpret_term(term) for term in self.enumerated_result]
        )


if __name__ == "__main__":
    unittest.main()
