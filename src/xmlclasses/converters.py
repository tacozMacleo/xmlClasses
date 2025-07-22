from __future__ import annotations

import dataclasses
import datetime
import enum
import types
import typing
import uuid
import xml.etree.ElementTree as ET

from .base_types import XmlAttributeField
from .base_types import XmlBaseType
from .base_types import XmlElementField
from .base_types import XmlTextField
from .error_handlers import error_handler


class XmlBaseClass:
    __dataclass_fields__: typing.ClassVar[dict[str, typing.Any]]

    @classmethod
    def from_element(cls, dom: ET.Element) -> typing.Self:
        arguments: dict = {}
        for key, field in cls.__dataclass_fields__.items():
            if not isinstance(field, XmlElementField | XmlAttributeField | XmlTextField):
                with error_handler(dom, cls.__name__):
                    msg = f"Expected XmlElementField or XmlAttributeField. Found: {type(field)}"
                    raise ValueError(msg)
            arguments[key] = _get_value(field, dom, cls.__name__)

        return cls(**arguments)

    @classmethod
    def from_string(cls, string: str) -> typing.Self:
        dom = ET.fromstring(string.strip())  # NOTE: Is unsecure, but do not want to import defusedxml
        return cls.from_element(dom)


def _get_child_from(tag: str, dom: ET.Element, *, single: bool = False) -> list[ET.Element] | ET.Element:
    if not single:
        return [x for x in dom if x.tag == tag]

    for child in dom:
        if child.tag == tag:
            return child
    msg = f"Could not find {tag} in {dom.tag}"
    raise ValueError(msg)


def _get_name(field: XmlBaseType) -> str:
    return field.alias if field.alias != dataclasses.MISSING else field.name


def _get_data(
    field: XmlBaseType,
    dom: ET.Element,
    name: str,
    *,
    single: bool = True,
) -> str | None | ET.Element | list[ET.Element]:
    field_alias = _get_name(field)

    if isinstance(field, XmlElementField):
        return _get_child_from(field_alias, dom, single=single)
    if isinstance(field, XmlAttributeField):
        return dom.attrib[field_alias]
    if isinstance(field, XmlTextField):
        return dom.text

    unknown_msg = f"Unknown field type: {type(field)}"
    raise ValueError(unknown_msg)


def _handle_none(field: XmlBaseType, dom: ET.Element, name: str):
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:
        return field.default_factory()
    return None

def _handle_union(field: XmlBaseType, dom: ET.Element, name: str):
    field_type: types.UnionType = field.type
    field_alias = _get_name(field)

    child_tags = {x.tag for x in dom}
    if field_alias not in dom.keys() and field_alias not in child_tags and not isinstance(field, XmlTextField):
        if types.NoneType not in typing.get_args(field_type):
            msg = f"Missing {field_alias} in {dom.tag}, with attributes {dom.attrib} and children {child_tags}"
            raise ValueError(msg)
        return _handle_none(field, dom, name)

    for d_type in typing.get_args(field_type):
        try:
            return _convert(d_type, field_alias, _get_data(field, dom, name), dom)
            break
        except ValueError:
            pass
    else:
        msg = f"Unable to convert {field_alias} to any of {typing.get_args(field_type)}"
        with error_handler(dom, name):
            raise ValueError(msg)


def _handle_generic_alias(field: XmlBaseType, dom: ET.Element, name: str) -> list | tuple | set:
    field_type = field.type
    field_alias = _get_name(field)

    if typing.get_origin(field_type) is list:
        return [_convert(typing.get_args(field_type)[0], field_alias, x, x) for x in _get_child_from(field_alias, dom)]

    if typing.get_origin(field_type) is tuple:
        data = list(_get_child_from(field_alias, dom))
        if len(typing.get_args(field_type)) != len(data):
            msg = f"Tuple expected {len(typing.get_args(field_type))} elements. Found: {len(data)}"
            raise ValueError(msg)

        return tuple(
            _convert(typing.get_args(field_type)[0], field_alias, d_data, d_data)
            for d_type, d_data in zip(typing.get_args(field_type), data, strict=True)
        )

    if typing.get_origin(field_type) is set:
        msg = "Sets are not supported"
        raise NotImplementedError(msg)

    # if typing.get_origin(field_type) is dict:  # TODO: FIXME!
    #     return dict(map(cls.__get_value, typing.get_args(field_type), _get_child_from(field_alias, dom)))

    msg = f"Unknown generic alias type: {field_type}"
    raise ValueError(msg)


def _handle_xml_base_field(field: XmlBaseType, dom: ET.Element, name: str):
    field_type = field.type
    field_alias = _get_name(field)

    sub_dom = list(_get_child_from(field_alias, dom))
    if len(sub_dom) != 1:
        msg = f'Expected exactly one "{field_alias}" element. Found: {len(sub_dom)}'
        raise ValueError(msg)
    print(field_alias, sub_dom[0])
    return _convert(field_type, field_alias, sub_dom[0], dom)


def _get_value(field: XmlBaseType, dom: ET.Element, name: str):
    # TODO: test for 'XmlTextField', 'XmlElementField' and 'XmlAttributeField' first.
    field_type = field.type
    field_alias = _get_name(field)

    if typing.get_origin(field_type) == typing.Literal:
        return _convert(field_type, field_alias, dom.attrib[field_alias], dom)

    if isinstance(field_type, types.UnionType):  # TODO: TEST ME!!
        return _handle_union(field, dom, name)

    if isinstance(field_type, types.GenericAlias):
        return _handle_generic_alias(field, dom, name)

    if isinstance(field, XmlTextField):
        return _convert(field_type, field_alias, dom.text.strip(), dom)

    if field_type is None:  # UNSURE: Do this make sense?
        return _handle_none(field, dom, name)

    if issubclass(field_type, XmlBaseClass):
        return _handle_xml_base_field(field, dom, name)

    return _convert(field_type, field_alias, dom.attrib[field_alias], dom)



# TODO: Change this to take make use of the more modern typing features.
T = typing.TypeVar("T", str, int, float, bool, datetime.datetime, uuid.UUID, XmlBaseClass, None)


def _convert(
    field_type: type[T],
    field_alias: str,
    data: str | ET.Element,
    dom: ET.Element,
) -> T | str:
    converter_dict: dict[type[T], typing.callable[[str], T]] = {
        int: lambda x: int(x),
        float: lambda x: float(x),
        str: lambda x: str(x),
        bool: lambda x: x.lower() in ["true", "1", "yes", "on"],
        datetime.datetime: lambda x: datetime.datetime.fromisoformat(x),
        uuid.UUID: lambda x: uuid.UUID(x),
        XmlBaseClass: lambda x: XmlBaseClass.from_string(x),
        None: lambda _: None,
        types.NoneType: lambda _: None,
        typing.Any: lambda x: x,
    }
    with error_handler(dom, field_alias):
        if isinstance(data, ET.Element):
            if issubclass(field_type, XmlBaseClass):
                return field_type.from_element(data)
            msg = f"Expected XmlBaseClass. Found: {field_type}"
            raise ValueError(msg)

        if typing.get_origin(field_type) == typing.Literal:
            if data in typing.get_args(field_type):
                return data
            msg = f"Literal value {data} not in {typing.get_args(field_type)}"
            raise ValueError(msg)

        if type(field_type) is not enum.EnumMeta:
            return converter_dict[field_type](data)

        if type(field_type) is enum.EnumMeta:
            return field_type(data)

        msg = f"Unknown type: {field_type}"
        raise ValueError(msg)
