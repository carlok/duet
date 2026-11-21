from soup.laws import enumerate_laws


def test_one_op_laws_order_4():
    # Equational Theories Project: 4694 laws of order <= 4 in one binary operation (x = x included)
    assert len(enumerate_laws(4, ('f',))) + 1 == 4694
