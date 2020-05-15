"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new instance of the Names class."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Chang", "Ethan", "Ilakya"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    for name in name_string_list:
        my_name.lookup([name])
    return my_name


def test_get_string_raises_exceptions(used_names):
    """Test if get_name_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Chang"),
    (1, "Ethan"),
    (2, "Ilakya"),
    (3, None)
])
def test_get_string(used_names, new_names, name_id, expected_string):
    """Test if get_name_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None
