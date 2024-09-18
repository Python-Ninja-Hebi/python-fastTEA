from typing import List, Dict, Any, Union
from . import Element
from .html import div, button as html_button

def add_bootstrap_class(element: Element, bootstrap_class: str):
    if 'class' in element.attributes:
        element.attributes['class'] += f" {bootstrap_class}"
    else:
        element.attributes['class'] = bootstrap_class
    return element

def container(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_bootstrap_class(div(attributes, children), "container")

def row(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_bootstrap_class(div(attributes, children), "row")

def col(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_bootstrap_class(div(attributes, children), "col")

def card(attributes: Dict[str, Any],children: Union[List[Element], Element, str]) -> Element:
    return add_bootstrap_class(div(attributes, children), "card")

def button(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return add_bootstrap_class(html_button(attributes, children), "btn btn-primary")

def alert(attributes: Dict[str, Any], children: Union[List[Element], Element, str], alert_type: str = "primary") -> Element:
    return add_bootstrap_class(div(attributes, children), f"alert alert-{alert_type}")
