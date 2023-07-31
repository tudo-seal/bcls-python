import logging
import unittest
from bcls import (
    Type,
    Constructor,
    Arrow,
    Intersection,
    BooleanTerm,
    Var,
    FiniteCombinatoryLogic,
    enumerate_terms,
    Subtypes,
)


class TestExampleCC(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(module)s %(levelname)s: %(message)s",
        # level=logging.INFO,
    )

    def test_CC(self) -> None:
        a: Type = Constructor("a")
        b: Type = Constructor("b")
        c: Type = Constructor("c")

        repository: dict[str, Type] = dict(
            {
                "C": Intersection(Arrow(a, b), Intersection(a, Intersection(b, c))),
            }
        )
        environment: dict[str, set[str]] = dict()
        subtypes = Subtypes(environment)

        # target: BooleanTerm[Type] = And(b, Not(And(a, c)))

        target: BooleanTerm[Type] = Var(b) & ~(Var(a) & Var(c))

        fcl = FiniteCombinatoryLogic(repository, subtypes)
        result = fcl.inhabit(target)

        enumerated_result = list(enumerate_terms(target, result))

        self.assertEqual(1, len(enumerated_result))

        for real_result in enumerated_result:
            self.logger.info(real_result)
            self.assertEqual(("C", (("C", ()),)), real_result)

        # if result.check_empty(target_type):
        #     self.logger.info("No inhabitants")
        # else:
        #     for tree in result[target_type][0:10]:
        #         self.logger.info(tree)
        #         self.logger.info("")


if __name__ == "__main__":
    unittest.main()
