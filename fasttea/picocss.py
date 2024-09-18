from typing import List, Dict, Any, Union
from . import Element
from .html import div, button as html_button

def add_pico_class(element: Element, pico_class: str):
    if 'class' in element.attributes:
        element.attributes['class'] += f" {pico_class}"
    else:
        element.attributes['class'] = pico_class
    return element

def container(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(div(attributes, children), "container")

def grid(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(div(attributes, children), "grid")

def card(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(Element("article", attributes, children), "card")

def progress(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(Element("progress", attributes, children), "progress")
