from dataclasses import dataclass
from typing import Literal
from xmlclasses import field
from xmlclasses import XmlBaseClass
from xmlclasses import XmlParserError
import pytest
from enum import Enum


def test_with_string() -> None:
    xml_with_string = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        data
    </root>
    """

    @dataclass
    class RootString(XmlBaseClass):
        data: str = field(text=True)

    root = RootString.from_string(xml_with_string.strip())
    assert isinstance(root.data, str)
    assert root.data == "data"


def test_with_int() -> None:
    xml_with_string = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        42
    </root>
    """

    @dataclass
    class RootString(XmlBaseClass):
        data: int = field(text=True)

    root = RootString.from_string(xml_with_string.strip())
    assert isinstance(root.data, int)
    assert root.data == 42


def test_with_float() -> None:
    xml_with_string = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        42.22
    </root>
    """

    @dataclass
    class RootString(XmlBaseClass):
        data: float = field(text=True)

    root = RootString.from_string(xml_with_string.strip())
    assert isinstance(root.data, float)
    assert root.data == 42.22


def test_with_attribute() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    @dataclass
    class RootAttribute(XmlBaseClass):
        value: str = field(attribute=True)

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.value, str)
    assert root.value == "data"


def test_with_element() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: Value = field(element=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value.data, str)
    assert isinstance(root.value, Value)
    assert root.value.data == "data"


def test_with_attribute_alias() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    @dataclass
    class RootAttribute(XmlBaseClass):
        new_name: str = field(alias="value", attribute=True)

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.new_name, str)
    assert root.new_name == "data"


def test_with_element_alias() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        new_name: str = field(alias="data", text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        nested: Value = field(alias="value", element=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.nested.new_name, str)
    assert isinstance(root.nested, Value)
    assert root.nested.new_name == "data"




def test_with_literal() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    @dataclass
    class RootAttribute(XmlBaseClass):
        new_name: Literal["data"] = field(alias="value", attribute=True)

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.new_name, str)
    assert root.new_name == "data"


def test_with_enum() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    class DataEnum(Enum):
        DATA = "data"
        NO_DATA = "no_data"

    @dataclass
    class RootAttribute(XmlBaseClass):
        new_name: DataEnum = field(alias="value", attribute=True)

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.new_name, DataEnum)
    assert root.new_name == DataEnum.DATA


def test_with_element_list() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data1</value>
        <value>data2</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: list[Value] = field(element=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value, list)
    assert len(root.value) == 2
    assert root.value[0].data == "data1"
    assert root.value[1].data == "data2"


def test_with_element_tuple() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data1</value>
        <value>data2</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: tuple[Value, Value] = field(element=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value, tuple)
    assert len(root.value) == 2
    assert root.value[0].data == "data1"
    assert root.value[1].data == "data2"


def test_with_element_list_with_text_field_union() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
        <value>2</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: int | str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: list[Value] = field(element=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value, list)
    assert len(root.value) == 2
    assert root.value[0].data == "data"
    assert root.value[1].data == 2


def test_with_element_list_with_attribute_union() -> None:
    xml_with_int = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="2">
    </root>
    """
    xml_with_str = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data">
    </root>
    """


    @dataclass
    class RootElement(XmlBaseClass):
        value: int | str = field(attribute=True)

    root = RootElement.from_string(xml_with_int.strip())
    assert isinstance(root.value, int)
    assert root.value == 2

    root = RootElement.from_string(xml_with_str.strip())
    assert isinstance(root.value, str)
    assert root.value == "data"




def test_optional_attribute() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: Value = field(element=True)
        not_value: str | None = field(attribute=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value.data, str)
    assert root.value.data == "data"
    assert root.not_value is None


def test_optional_element() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: Value = field(element=True)
        not_value: Value | None = field(element=True)

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value.data, str)
    assert root.value.data == "data"
    assert root.not_value is None


def test_fail_on_data_flatting_element() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>
            <subValue>
                data
            </subValue>
        </value>
    </root>
    """

    @dataclass
    class Value(XmlBaseClass):
        data: str = field(text=True)

    @dataclass
    class RootElement(XmlBaseClass):
        value: Value = field(alias="subValue", element=True)

    with pytest.raises(ValueError):
        RootElement.from_string(xml_with_element.strip())
