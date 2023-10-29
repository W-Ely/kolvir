import json

import pytest

from kolvir.util.dot_dict import DotDict


def test_dot_dict_is_dict():
    dot_dict = DotDict()
    assert isinstance(dot_dict, dict)


def test_dot_dict_can_set_attribute_by_dot_notation():
    dot_dict = DotDict()
    dot_dict.test = "test"
    assert dot_dict.test == "test"
    assert dot_dict["test"] == "test"


def test_dot_dict_is_json_dumpsable():
    dot_dict = DotDict()
    dot_dict.test = "test"
    assert json.dumps(dot_dict) == '{"test": "test"}'


def test_dot_dict_setattr():
    dot_dict = DotDict()
    setattr(dot_dict, "test", "test")
    assert dot_dict.test == "test"
    assert dot_dict["test"] == "test"


def test_dot_dict_getattr():
    dot_dict = DotDict()
    dot_dict.test = "test"
    assert getattr(dot_dict, "test") == "test"


def test_dot_dict_updateable():
    dot_dict = DotDict()
    dot_dict.test = "test"
    dot_dict2 = DotDict()
    dot_dict2.dot = "dict"
    dot_dict.update(dot_dict2)
    assert dot_dict.dot == "dict"
    assert dot_dict.test == "test"


def test_dot_dict_not_founds():
    dot_dict = DotDict()
    with pytest.raises(AttributeError):
        dot_dict.not_found  # pylint: disable=pointless-statement
    with pytest.raises(KeyError):
        dot_dict["not_found"]  # pylint: disable=pointless-statement


def test_dot_dict_instantiate_with_dict():
    dot_dict = DotDict({"dot": "dict"})
    assert dot_dict.dot == "dict"
    assert dot_dict["dot"] == "dict"


def test_dot_dict_instantiate_kwargs():
    dot_dict = DotDict(**{"dot": "dict"})
    assert dot_dict.dot == "dict"
    assert dot_dict["dot"] == "dict"


def test_dot_dict_get_with_default():
    dot_dict = DotDict()
    assert dot_dict.get("dot", "dict") == "dict"
