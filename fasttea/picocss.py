from typing import List, Dict, Any, Union
from . import Element
from .html import div, input_

def add_pico_class(element: Element, pico_class: str, more_attributes:Dict[str,str] | None = None):
    if len(pico_class)>0:
        if 'class' in element.attributes:
            element.attributes['class'] += f" {pico_class}"
        else:
            element.attributes['class'] = pico_class

    if more_attributes:
        for key, value in more_attributes.items():
            if key not in element.attributes:
                element.attributes[key] = value

    return element

def container(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(div(attributes, children), "container")

def container_fluid(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(div(attributes, children), "container-fluid")

def grid(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(div(attributes, children), "grid")

def card(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(Element("article", attributes, children), "card")

def progress(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(Element("progress", attributes, children), "progress")

def switch(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(Element("input", attributes, children), "", {"type":"checkbox", "role":"switch"})

def group(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(div(attributes, children), "", {"role":"group"})

def search(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_pico_class(input_(attributes, children), "", {"type":"search"})