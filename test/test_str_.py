from xmlclasses import XmlClass
from xmlclasses import XmlTextField



def test_str() -> None:
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
    string = str(root)
    assert string == """RootElement(
    value=Value(
        data='data'
    )
)"""
