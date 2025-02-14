from collections.abc import Callable
import logging
import unittest
from bcls import Type, Constructor, Arrow, Intersection, inhabit_and_interpret


class TestWrongSpec2(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(module)s %(levelname)s: %(message)s",
        # level=logging.INFO,
    )

    def test_wrong_spec(self) -> None:
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
                F: Intersection(Arrow(a, Arrow(d, b)), Arrow(d, Intersection(a, c))),
            }
        )

        with self.assertRaises(RuntimeError):
            for real_result in inhabit_and_interpret(repository, b):
                self.logger.info(real_result)


if __name__ == "__main__":
    unittest.main()
