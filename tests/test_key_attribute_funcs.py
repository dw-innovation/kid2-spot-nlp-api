import unittest

from app.adopt_generation import apply_rule


class TestKeyAtt(unittest.TestCase):

    def test_assign_combination(self):
        example = "italian restaurant"
        assert apply_rule(example)

        example = "french restaurant"
        assert apply_rule(example)

        example = "italian eatery"
        assert apply_rule(example)

        example = "french eatery"
        assert apply_rule(example)

        example = "wind turbine"
        assert not apply_rule(example)

    if __name__ == '__main__':
        unittest.main()
