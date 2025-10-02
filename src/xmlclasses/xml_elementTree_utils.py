import xml.etree.ElementTree as ET


def _get_child_from(tag: str, dom: ET.Element, *, single: bool = False) -> list[ET.Element] | ET.Element:
    if not single:
        return [x for x in dom if x.tag == tag]

    for child in dom:
        if child.tag == tag:
            return child
    msg = f'Could not find "{tag}" in "{dom.tag}"'
    raise ValueError(msg)
