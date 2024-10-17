from typing import List, Dict, Any, Union
from . import Element

def text(content: str) -> str:
    return content

def div(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("div", attributes, children)

def span(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("span", attributes, children)

def h1(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("h1", attributes, children)

def h2(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("h2", attributes, children)

def h3(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("h3", attributes, children)

def p(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("p", attributes, children)

def button(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("button", attributes, children)

def fieldset(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("fieldset", attributes, children)

def canvas(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("canvas", attributes, children)

def a(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("a", attributes, children)

def i(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("i", attributes, children)

def img(attributes: Dict[str, Any], children: Union[List[Element], Element, str] = "") -> Element:
    return Element("img", attributes, children)

def ul(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("ul", attributes, children)

def ol(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("ol", attributes, children)

def li(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("li", attributes, children)

def table(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("table", attributes, children)

def tr(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("tr", attributes, children)

def td(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("td", attributes, children)

def th(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("th", attributes, children)

def form(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("form", attributes, children)

def input_(attributes: Dict[str, Any], children: Union[List[Element], Element, str] = "") -> Element:
    return Element("input", attributes, children)

def textarea(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("textarea", attributes, children)

def select(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("select", attributes, children)

def option(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("option", attributes, children)

def label(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("label", attributes, children)

def header(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("header", attributes, children)

def footer(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("footer", attributes, children)

def nav(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("nav", attributes, children)

def section(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("section", attributes, children)

def article(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("article", attributes, children)

def aside(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("aside", attributes, children)

def main(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("main", attributes, children)

def hr(attributes: Dict[str, Any], children: Union[List[Element], Element, str] = "") -> Element:
    return Element("hr", attributes, children)

def br(attributes: Dict[str, Any], children: Union[List[Element], Element, str] = "") -> Element:
    return Element("br", attributes, children)