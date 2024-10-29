from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Callable, Dict, Any, List, Union
from enum import Enum
import os
import toml
from rich import print


class CSSFramework(Enum):
    NONE = ''
    PICO = '<link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2.*/css/pico.min.css">'
    BOOTSTRAP = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">'
    TAILWIND = '<script src="https://cdn.tailwindcss.com"></script>'  #Tailwind CSS as an option


# region TEA
class Model(BaseModel):
    """Base class for the application state"""
    pass


class Msg(BaseModel):
    """Base class for messages"""
    action: str
    value: Any = None


class Cmd(BaseModel):
    """Base class for commands"""
    action: str
    payload: Dict[str, Any] = {}
    # New field for automatic message sending
    return_msg: Union[Msg, None] = None


# endregion

# region html
class Element:
    _id: int = 0

    def __init__(self, tag: str,
                 attributes: Dict[str, Any],
                 children: Union[List['Element'], 'Element', str]):
        self.tag = tag
        self.attributes = attributes
        self.children = children if isinstance(children, list) else [children]

    def to_htmx(self) -> str:
        self.add_htmx_attributes()
        attrs = ' '.join(f"{k}='{v}'" for k, v in self.attributes.items() if v is not None)
        children_html = ''.join(
            child.to_htmx() if isinstance(child, Element) else str(child) for child in self.children)
        return f"<{self.tag} {attrs}>{children_html}</{self.tag}>"

    def test_add_htmx_attribute(self, attribut: str, value: str):
        if attribut not in self.attributes:
            self.attributes[attribut] = value

    def add_htmx_attributes(self):
        """Add HTMX attributes to elements with onClick, onChanging or onChange handlers"""
        if 'onClick' in self.attributes:
            action = self.attributes['onClick']
            self.attributes.pop('onClick')

            if 'getValue' in self.attributes:
                id = self.attributes['getValue']
                self.attributes.pop('getValue')
                self.attributes[
                    "hx-vals"] = f'js:{{"action": "{action}","value": document.getElementById("{id}").value}}'
            else:
                self.attributes["hx-vals"] = f'{{"action": "{action}"}}'

            self.attributes.update({
                "hx-post": "/update",
                "hx-trigger": "click",
                "hx-swap": "innerHTML"
            })
            self.test_add_htmx_attribute("hx-target", "#app")

        elif 'onChange' in self.attributes or 'onChanging' in self.attributes:
            if 'onChange' in self.attributes:
                action = self.attributes['onChange']
                self.attributes.pop('onChange')
                trigger = "change"
            else:
                action = self.attributes['onChanging']
                self.attributes.pop('onChanging')
                trigger = "keyup changed delay:500ms"

            if 'id' not in self.attributes:
                self.attributes['id'] = self.create_id()

            id = self.attributes['id']

            self.attributes.update({
                "hx-post": "/update",
                "hx-trigger": trigger,
                "hx-vals": f'js:{{"action": "{action}","value": document.getElementById("{id}").value}}',
                "hx-swap": "innerHTML"
            })
            self.test_add_htmx_attribute("hx-target", "#app")

    def create_id(self) -> str:
        value = f'id{Element._id}'
        Element._id += 1
        return value


# endregion

# region uibubble
class UIBubble:
    def __init__(self, css_framework: CSSFramework):
        self.css_framework = css_framework

    def render(self) -> Element:
        raise NotImplementedError("Subclasses must implement this method")


# endregion

# region htmlbubble
class HtmlBubble:
    def __init__(self, name: str, js_libraries: List[str], class_definition: str):
        self.name = name
        self.js_libraries = js_libraries
        self.class_definition = class_definition


#endregion

class FastTEA:
    def __init__(self, initial_model: Model,
                 css_framework: CSSFramework = CSSFramework.NONE,
                 js_libraries: List[str] = [],
                 css_additional: List[str] = [],
                 debug=False):
        self.app = FastAPI()
        self.model = initial_model
        self.update_fn: Callable[[Msg, Model], tuple[Model, Union[Cmd, None]]] = lambda msg, model: (model, None)
        self.view_fn: Callable[[Model], Element] = lambda model: Element("div", {}, [])
        self.css_framework = css_framework
        self.js_libraries = js_libraries
        self.css_additional = css_additional
        self.html_bubbles: List[HtmlBubble] = []
        self.cmd_handlers: Dict[str, Callable] = {}  #dictionary to store command handlers
        self.debug = debug

        file_path = './.fasttea/security.toml'
        self.security = {}

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    security_data = toml.load(file)
                    self.security.update(security_data)
            except Exception as e:
                print(f"Reading file: {e}")

        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            if self.debug: print('fastTEA root')
            css_link = self._get_css_link()
            css_links = self._get_css_links()
            js_links = self._get_js_links()
            js_links_from_html_bubbles = self._get_js_links_from_html_bubbles()
            value = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <script src="https://unpkg.com/htmx.org@2.0.2"></script>
                    {css_link}
                    {css_links}
                    {js_links}
                    {js_links_from_html_bubbles}
                    <title>fastTEA Application</title>
                </head>
                 <body>
                        <main class="container">
                            <div id="app" hx-get="/init" hx-trigger="load, update from:body"></div>
                        </main>
                        <script>
                            // Helper function for triggering HTMX events with message data
                           function triggerMsg(action, value) {{
                                htmx.ajax('POST', '/update', {{
                                    target: '#app',
                                    swap: 'innerHTML',
                                    values: {{
                                        action: action,
                                        value: value
                                    }}
                                }});
                            }}
                            
                            {self.html_bubble_classes_js}
                            {self.generate_cmd_handlers_js}
                            const app = {{
                                executeCmd(cmd) {{
                                    if (cmd.action in this.cmdHandlers) {{
                                        const result = this.cmdHandlers[cmd.action](cmd.payload);
                                        // If command handler returns a message definition, send it
                                        if (result && result.msg) {{
                                            triggerMsg(result.msg.action, result.msg.value);
                                        }}
                                    }} else {{
                                        console.error(`No handler for command: ${{cmd.action}}`);
                                    }}
                                }},
                                cmdHandlers: {{}}
                            }};
                            {self.add_cmd_handlers_js}
                            document.body.addEventListener('htmx:afterOnLoad', function(event) {{
                                const cmdData = event.detail.xhr.getResponseHeader('HX-Trigger');
                                if (cmdData) {{
                                    const cmd = JSON.parse(cmdData);
                                    app.executeCmd(cmd);
                                }}
                            }});
                        </script>
                        {self._get_js_link()}
                    </body>
                </html>
                """
            if self.debug:
                print(f'FastTEA root {value}')
            return value

        @self.app.get("/init")
        async def init():
            view_element = self.view_fn(self.model)
            return HTMLResponse(f"""
                                {view_element.to_htmx()}
                            """)

        @self.app.get("/static/{file_path:path}")
        async def get_file(file_path: str):
            base_path = "./static/"  # static path

            full_path = os.path.join(base_path, file_path)

            if not os.path.isfile(full_path):
                raise HTTPException(status_code=404, detail=f"File {full_path} not found")

            return FileResponse(full_path)

        @self.app.post("/update")
        async def update(request: Request):
            #content_type = request.headers.get('Content-Type', '')
            #print(f'content type {content_type}')

            form_data = await request.form()
            #print(f'form {form_data}')
            action = form_data.get("action")
            value = form_data.get("value")
            #print(f'action {action}')
            #print(f'value {value}')
            msg = Msg(action=action, value=value)
            new_model, cmd = self.update_fn(msg, self.model)
            self.model = new_model
            view_element = self.view_fn(self.model)
            response = HTMLResponse(view_element.to_htmx())
            if cmd:
                response.headers["HX-Trigger"] = cmd.json()
            return response

    def add_html_bubble(self, bubble: HtmlBubble) -> HtmlBubble:
        self.html_bubbles.append(bubble)
        return bubble

    @property
    def add_cmd_handlers_js(self):
        handlers = {}
        handlers.update({k: v.__name__ for k, v in self.cmd_handlers.items()})
        return "app.cmdHandlers = {" + ",".join(f"'{k}': {v}" for k, v in handlers.items()) + "};"

    @property
    def generate_cmd_handlers_js(self):
        #Generate JavaScript functions for new command handlers
        cmd_handlers_js = "\n".join(
            f"function {handler.__name__}(payload) {{ {handler(None)} }}" for handler in self.cmd_handlers.values())
        return cmd_handlers_js

    @property
    def html_bubble_classes_js(self):
        return "\n".join([i.class_definition for i in self.html_bubbles])

    @property
    def cmd_bubble_instances_js(self):
        instances = []
        for i in self.cmd_bubbles:
            instances.append(f"app.{i.name} = new {i.class_name}();")
        return "; ".join(instances)

    def update(self, update_fn: Callable[[Msg, Model], tuple[Model, Union[Cmd, None]]]):
        """Decorator to set the update function"""
        self.update_fn = update_fn
        return update_fn

    def view(self, view_fn: Callable[[Model], Element]):
        """Decorator to set the view function"""
        self.view_fn = view_fn
        return view_fn

    def cmd(self, action: str):
        """Decorator to handle cmd function"""

        def decorator(f: Callable):
            self.cmd_handlers[action] = f
            return f

        return decorator

    def _get_css_link(self):
        return self.css_framework.value

    def _get_js_links(self):
        return '\n'.join([f'<script src="{lib}"></script>' for lib in self.js_libraries])

    def _get_js_links_from_html_bubbles(self):
        js_libraries = []
        for i in self.html_bubbles:
            for j in i.js_libraries:
                js_libraries.append(j)
        js_libraries = list(set(js_libraries))
        return '\n'.join([f'<script src="{lib}"></script>' for lib in js_libraries])

    def _get_css_links(self):
        #<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css">
        return '\n'.join([f'<link rel="stylesheet" href="{lib}">' for lib in self.css_additional])

    def _get_js_link(self):
        if self.css_framework == CSSFramework.BOOTSTRAP:
            return '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>'
        else:
            return ''

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="127.0.0.1", port=5001)
