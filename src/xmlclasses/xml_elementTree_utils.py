import xml.etree.ElementTree as ET

from .base_types import XmlAttributeField
from .base_types import XmlBaseType
from .base_types import XmlElementField
from .base_types import XmlTextField

def _get_child_from(tag: str, dom: ET.Element, *, single: bool = False) -> list[ET.Element] | ET.Element:
    if not single:
        return [x for x in dom if x.tag == tag]

    for child in dom:
        if child.tag == tag:
            return child
    msg = f"Could not find {tag} in {dom.tag}"
    raise ValueError(msg)


def _get_data(
    name: str,
    field_type: XmlBaseType,
    dom: ET.Element,
    parent_name: str,
    *,
    single: bool = True,
) -> str | None | ET.Element | list[ET.Element]:
    if isinstance(field_type, XmlElementField):
        return _get_child_from(name, dom, single=single)
    if isinstance(field_type, XmlAttributeField):
        return dom.attrib[name]
    if isinstance(field_type, XmlTextField):
        return dom.text

    unknown_msg = f"Unknown field type: {type(field_type)}"
    raise ValueError(unknown_msg)
