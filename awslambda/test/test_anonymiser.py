"""
Tests for the Anonymiser module.
"""
import pytest

from awslambda.src.modules.anonymiser import Anonymiser


@pytest.fixture(name='subject')
def fixture_subject():
    """
    Return a default instance of the test subject class.
    :return (obj):  Default instance of the test subject class.
    """
    return Anonymiser()


@pytest.mark.parametrize("relative_vars, expected", [
    ((0.12429263442754745,
      0.23144002258777618,
      0.5118623375892639,
      0.20334899425506592), ((51, 20), (63, 43))),
    ((0.12429263442754745,
      0.23144002258777618,
      0.0018623375892639,
      0.0334899425506592), ((0, 3), (12, 26))),
])

def test_position_from_bounding_box(subject, relative_vars, expected):
    """
    Test the position_from_bounding_box() method.

    :param (obj)  subject:       Testing Fixture.
    :param (dict) relative_vars: Relative box location and dimension.
    :param (list) expected:      Expected test result.
    :return (None):
    """
    bounding_box = {
        "Width": relative_vars[0],
        "Height": relative_vars[1],
        "Left": relative_vars[2],
        "Top": relative_vars[3]
    }

    output = subject.position_from_bounding_box(bounding_box, 100, 100)
    assert output == expected


@pytest.mark.parametrize("box_coords, expected", [
    (((51, 20),
      (63, 43)),
     (57, 31)),
])

def test_find_box_centre(subject, box_coords, expected):
    """
    Test the find_box_centre method

    :param (obj)  subject:      Testing Fixture.
    :param (list) box_coords:   Co-ords to locate box at.
    :return (None):
    """
    output = subject.find_box_centre(box_coords)
    assert output == expected
