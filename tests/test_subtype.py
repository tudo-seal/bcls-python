import logging
import unittest
from bcls import Constructor
from bcls.subtypes import Subtypes
from bcls.types import Intersection


class TestSubtype(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(module)s %(levelname)s: %(message)s",
        # level=logging.INFO,
    )

    def test_constructor_refl(self) -> None:
        a = Constructor("A")
        subtypes = Subtypes({})
        self.assertTrue(subtypes.check_subtype(a, a))

    def test_idempotence_right(self) -> None:
        a = Constructor("A")

        subtypes = Subtypes({})
        self.assertTrue(subtypes.check_subtype(a, Intersection(a, a)))


if __name__ == "__main__":
    unittest.main()
