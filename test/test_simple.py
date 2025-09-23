from enum import Enum
from typing import Literal
import base64
import uuid

import pytest

from xmlclasses import XmlClass
from xmlclasses import XmlParserError
from xmlclasses import XmlTextField
# from xmlclasses import field


def test_with_string() -> None:
    xml_with_string = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        data
    </root>
    """

    class RootString(XmlClass):
        data: XmlTextField[str]

    root = RootString.from_string(xml_with_string.strip())
    assert isinstance(root.data, str)
    assert root.data == "data"


def test_with_int() -> None:
    int_value = 42
    xml_with_string = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        {int_value}
    </root>
    """

    class RootString(XmlClass):
        data: XmlTextField[int]

    root = RootString.from_string(xml_with_string.strip())
    assert isinstance(root.data, int)
    assert root.data == int_value


def test_with_float() -> None:
    float_value = 42.22
    xml_with_string = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        {float_value}
    </root>
    """

    class RootString(XmlClass):
        data: XmlTextField[float]

    root = RootString.from_string(xml_with_string.strip())
    assert isinstance(root.data, float)
    assert root.data == float_value


def test_with_cdata() -> None:  # CDATA
    xml_with_cdata = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
<![CDATA[
let message = (login == 'Employee') ? 'Hello' :
  (login == 'Director') ? 'Hello, boss' :
  (login == '') ? 'No login' :
  '';
]]>
    </root>
    """
    class RootElement(XmlClass):
        code: XmlTextField[str]

    root = RootElement.from_string(xml_with_cdata.strip())
    assert isinstance(root.code, str)
    assert root.code == (
        "let message = (login == 'Employee') ? 'Hello' :\n"
        "  (login == 'Director') ? 'Hello, boss' :\n"
        "  (login == '') ? 'No login' :\n"
        "  '';"
    )


# def test_with_bytes() -> None:
#     xml_with_base64 = """
#     <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
#     <root>
#         "443"
#     </root>
#     """

#     @dataclass
#     class RootString(XmlBaseClass):
#         data: bytes = field(text=True)

#     root = RootString.from_string(xml_with_base64.strip())
#     assert isinstance(root.data, float)
#     assert root.data == 42.22



def test_with_uuid() -> None:
    uuid_value = uuid.uuid4()
    xml_with_uuid = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        {uuid_value}
    </root>
    """

    class RootString(XmlClass):
        data: XmlTextField[uuid.UUID]

    root = RootString.from_string(xml_with_uuid.strip())
    assert isinstance(root.data, uuid.UUID)
    assert root.data == uuid_value




# UNSURE: Do this even make sense?
def test_with_none() -> None:
    xml_with_none = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root />
    """

    class RootString(XmlClass):
        data: None

    root = RootString.from_string(xml_with_none.strip())
    assert root.data is None



def test_with_attribute() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    class RootAttribute(XmlClass):
        value: str

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.value, str)
    assert root.value == "data"


def test_nested_element() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>
            <data>data</data>
        </value>
    </root>
    """

    class Data(XmlClass):
        data: XmlTextField[str]

    class Value(XmlClass):
        data: Data

    class RootElement(XmlClass):
        value: Value

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value.data.data, str)
    assert isinstance(root.value.data, Data)
    assert isinstance(root.value, Value)
    assert root.value.data.data == "data"


def test_with_element() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        value: Value

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value.data, str)
    assert isinstance(root.value, Value)
    assert root.value.data == "data"


# def test_with_attribute_alias() -> None:
#     xml_with_attribute = """
#     <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
#     <root value="data" />
#     """

#     class RootAttribute(XmlClass):
#         new_name: str = field(alias="value")

#     root = RootAttribute.from_string(xml_with_attribute.strip())
#     assert isinstance(root.new_name, str)
#     assert root.new_name == "data"


# def test_with_element_alias() -> None:
#     xml_with_element = """
#     <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
#     <root>
#         <value>data</value>
#     </root>
#     """

#     class Value(XmlClass):
#         data: XmlTextField[str]

#     class RootElement(XmlClass):
#         nested: Value

#     root = RootElement.from_string(xml_with_element.strip())
#     assert isinstance(root.nested.data, str)
#     assert isinstance(root.nested, Value)
#     assert root.nested.data == "data"




def test_with_literal() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    class RootAttribute(XmlClass):
        value: Literal["data"]

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.value, str)
    assert root.value == "data"


def test_with_enum() -> None:
    xml_with_attribute = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="data" />
    """

    class DataEnum(Enum):
        DATA = "data"
        NO_DATA = "no_data"

    class RootAttribute(XmlClass):
        value: DataEnum

    root = RootAttribute.from_string(xml_with_attribute.strip())
    assert isinstance(root.value, DataEnum)
    assert root.value == DataEnum.DATA


def test_with_element_list() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data1</value>
        <value>data2</value>
    </root>
    """
    value_count = 2

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        value: list[Value]

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value, list)
    assert len(root.value) == value_count
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
    value_count = 2


    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        value: tuple[Value, Value]

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value, tuple)
    assert len(root.value) == value_count
    assert root.value[0].data == "data1"
    assert root.value[1].data == "data2"


def test_with_element_set() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data1</value>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        value: set[Value]

    with pytest.raises(NotImplementedError, match="Sets are not supported"):
        RootElement.from_string(xml_with_element.strip())



def test_with_element_list_with_text_field_union() -> None:
    the_int = 2
    the_str = "data"
    value_count = 2

    xml_with_element = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>{the_str}</value>
        <value>{the_int}</value>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[int | str]

    class RootElement(XmlClass):
        value: list[Value]

    root = RootElement.from_string(xml_with_element.strip())
    assert isinstance(root.value, list)
    assert len(root.value) == value_count
    assert root.value[0].data == the_str
    assert root.value[1].data == the_int


def test_with_element_list_with_attribute_union() -> None:
    the_int = 2
    the_str = "data"

    xml_with_int = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="{the_int}">
    </root>
    """
    xml_with_str = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root value="{the_str}">
    </root>
    """


    class RootElement(XmlClass):
        value: int | str

    root = RootElement.from_string(xml_with_int.strip())
    assert isinstance(root.value, int)
    assert root.value == the_int

    root = RootElement.from_string(xml_with_str.strip())
    assert isinstance(root.value, str)
    assert root.value == the_str




def test_optional_attribute() -> None:
    xml_with_element = """
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        <value>data</value>
    </root>
    """

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        value: Value
        not_value: str | None

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

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        value: Value
        not_value: Value | None

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

    class Value(XmlClass):
        data: XmlTextField[str]

    class RootElement(XmlClass):
        sub_value: Value

    with pytest.raises(XmlParserError, match='Expected exactly one "sub_value" element. Found: 0'):
        RootElement.from_string(xml_with_element.strip())


def test_decoder_with_base64() -> None:
    data = "42.22"
    xml_with_base64 = f"""
    <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
    <root>
        {base64.b64encode(data.encode()).decode()}
    </root>
    """

    class RootString(XmlClass):
        data: XmlTextField[base64.b64decode]

    root = RootString.from_string(xml_with_base64.strip())
    assert isinstance(root.data, bytes)
    assert root.data.decode() == data

