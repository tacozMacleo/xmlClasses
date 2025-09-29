from typing import Literal
import re
import pytest

from xmlclasses import XmlClass
from xmlclasses import XmlParserError
from xmlclasses import XmlTextField


def test_with_boolean() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="kjgs" />
    """

    class RootAttribute(XmlClass):
        value: bool

    with pytest.raises(
        XmlParserError,
        match=re.escape(
            "Error in \"value\" while parsing tag: \"root\", with attributes: {'value': 'kjgs'}\nBoolean value kjgs not in ['true', '1', 'yes', 'on'] or ['false', '0', 'no', 'off']"
        ),
    ):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_with_literal() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="notData" />
    """

    class RootAttribute(XmlClass):
        value: Literal["data"]

    with pytest.raises(XmlParserError, match=r"Literal value \"notData\" not in the defined values: \('data',\)"):
        RootAttribute.from_string(xml_with_attribute.strip())


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

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        sub_value: Value

    with pytest.raises(XmlParserError, match=r'Could not find "sub_value" in "root"'):
        RootElement.from_string(xml_with_element.strip())


def test_unknown_type() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="kjgs" />
    """

    class RootAttribute(XmlClass):
        value: pytest

    with pytest.raises(XmlParserError, match=re.escape("Unknown type: pytest")):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_union_covert_error() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="kjgs"/>
    """

    class RootAttribute(XmlClass):
        value: int | float

    with pytest.raises(
        XmlParserError, match=re.escape('Unable to convert "value"\'s value: "kjgs" to any of (int, float)')
    ):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_text_field_covert_error() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        kjgs
    </root>
    """

    class RootAttribute(XmlClass):
        value: XmlTextField[int | float]

    with pytest.raises(
        XmlParserError, match=re.escape('Unable to convert "value"\'s value: "kjgs" to any of (int, float)')
    ):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_missing_tuple_element() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
        <extra>data</extra>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootAttribute(XmlClass):
        value: tuple[Value, Value]

    with pytest.raises(XmlParserError, match=re.escape("Tuple expected 2 elements. Found: 1")):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_extra_tuple_element() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
        <value>data</value>
        <value>data</value>
        <extra>data</extra>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootAttribute(XmlClass):
        value: tuple[Value, Value]

    with pytest.raises(XmlParserError, match=re.escape("Tuple expected 2 elements. Found: 3")):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_extra_attribute() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="kjgs" extra="kjgs" />
    """

    class RootAttribute(XmlClass):
        value: str

    with pytest.raises(XmlParserError, match=re.escape("Extra attribute: extra")):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_missing_attribute_union() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root/>
    """

    class RootAttribute(XmlClass):
        value: int | float

    with pytest.raises(
        XmlParserError, match=re.escape('Missing "value" in "root", with attributes: {} and children: ')
    ):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_missing_attribute() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root/>
    """

    class RootAttribute(XmlClass):
        value: int

    with pytest.raises(XmlParserError, match=re.escape('Missing attribute: "value"')):
        RootAttribute.from_string(xml_with_attribute.strip())


def test_extra_text_field() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data">data</root>
    """

    class RootAttribute(XmlClass):
        value: str

    with pytest.raises(XmlParserError, match=re.escape("Extra text field: data")):
        RootAttribute.from_string(xml_with_attribute.strip())




def test_extra_element() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
        <extra>data</extra>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootAttribute(XmlClass):
        value: Value

    with pytest.raises(XmlParserError, match=re.escape("Extra element: extra")):
        RootAttribute.from_string(xml_with_attribute.strip())


