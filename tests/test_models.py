from distributions.models import Formula
from distributions.models import Distribution

def test_formula():
    formula = Formula()
    assert formula.mad_constant == 0


