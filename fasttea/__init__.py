from fastapi import FastAPI , Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Callable, Dict, Any, List, Union
from enum import Enum
import os
import toml
from rich import print

class CSSFramework(Enum):
    NONE = 0
    PICO = 1
    BOOTSTRAP = 2
    TAILWIND = 3  #Tailwind CSS as an option

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

class Element:
    _id:int = 0

    def __init__(self, tag: str,
                 attributes: Dict[str, Any],
                 children: Union[List['Element'], 'Element', str]):
        self.tag = tag
        self.attributes = attributes
        self.children = children if isinstance(children, list) else [children]

    def to_htmx(self) -> str:
        self.add_htmx_attributes()
        attrs = ' '.join(f"{k}='{v}'" for k, v in self.attributes.items() if v is not None)
        children_html = ''.join(child.to_htmx() if isinstance(child, Element) else str(child) for child in self.children)
        return f"<{self.tag} {attrs}>{children_html}</{self.tag}>"

    def add_htmx_attributes(self):
        """Add HTMX attributes to elements with onClick or onChange handlers"""
        if 'onClick' in self.attributes:
            action = self.attributes['onClick']
            self.attributes.pop('onClick')

            if 'getValue' in self.attributes:
                id = self.attributes['getValue']
                self.attributes.pop('getValue')
                self.attributes["hx-vals"] = f'js:{{"action": "{action}","value": document.getElementById("{id}").value}}'
            else:
                self.attributes["hx-vals"] = f'{{"action": "{action}"}}'

            self.attributes.update({
                "hx-post": "/update",
                "hx-trigger" : "click",
                "hx-target": "#app",
                "hx-swap": "innerHTML"
            })
        elif 'onChange' in self.attributes:
            action = self.attributes['onChange']
            self.attributes.pop('onChange')

            if 'id' not in self.attributes:
                self.attributes['id'] =  self.create_id()

            id = self.attributes['id']

            trigger = "change"
            if 'type' in self.attributes:
                if self.attributes['type'] == "text":
                    trigger = "keyup changed delay:500ms"

            self.attributes.update({
                "hx-post": "/update",
                "hx-trigger": trigger,
                "hx-vals": f'js:{{"action": "{action}","value": document.getElementById("{id}").value}}',
                "hx-target": "#app",
                "hx-swap": "innerHTML"
            })

    def create_id(self)->str:
        value = f'id{Element._id}'
        Element._id += 1
        return value

class UIBubble:
    def __init__(self, css_framework: CSSFramework):
        self.css_framework = css_framework

    def render(self) -> Element:
        raise NotImplementedError("Subclasses must implement this method")

class CmdBubble:
    def __init__(self, name):
        self.name = name
        self.handlers = {}
        self.init_js = ""

    def cmd(self, action):
        def decorator(f):
            self.handlers[action] = f.__name__
            return f
        return decorator

    def init(self, f):
        self.init_js = f()
        return f

class FastTEA:
    def __init__(self, initial_model: Model,
                 css_framework: CSSFramework = CSSFramework.NONE,
                 js_libraries: List[str] = [],
                 debug=False):
        self.app = FastAPI()
        self.model = initial_model
        self.update_fn: Callable[[Msg, Model], tuple[Model, Union[Cmd, None]]] = lambda msg, model: (model, None)
        self.view_fn: Callable[[Model], Element] = lambda model: Element("div", [], [])
        self.css_framework = css_framework
        self.js_libraries = js_libraries
        self.cmd_bubbles: List[CmdBubble] = []
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
            js_links = self._get_js_links()
            value = f"""
                <html>
                <head>
                    <script src="https://unpkg.com/htmx.org@2.0.2"></script>
                    {css_link}
                    {js_links}
                    <title>fastTEA Application</title>
                </head>
                <body>
                    <main class="container">
                        <div id="app" hx-get="/init" hx-trigger="load"></div>
                    </main>
                    <script>
                        {self.init_js}
                        const app = {{
                            executeCmd(cmd) {{
                                if (cmd.action in this.cmdHandlers) {{
                                    this.cmdHandlers[cmd.action](cmd.payload);
                                }} else {{
                                    console.error(`No handler for command: ${{cmd.action}}`);
                                }}
                            }},
                            cmdHandlers: {{}}
                        }};
                        {self.cmd_handlers_js}
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
            return HTMLResponse(view_element.to_htmx())

        @self.app.post("/update")
        async def update(request: Request):
            form_data = await request.form()
            action = form_data.get("action")
            value = form_data.get("value")
            print(f'value {value}')
            msg = Msg(action=action, value=value)
            new_model, cmd = self.update_fn(msg, self.model)
            self.model = new_model
            view_element = self.view_fn(self.model)
            response = HTMLResponse(view_element.to_htmx())
            if cmd:
                response.headers["HX-Trigger"] = cmd.json()
            return response

    def cmd_bubble(self, name):
        bubble = CmdBubble(name)
        self.cmd_bubbles.append(bubble)
        return bubble

    @property
    def cmd_handlers_js(self):
        handlers = {}
        for bubble in self.cmd_bubbles:
            handlers.update(bubble.handlers)
        handlers.update({k: v.__name__ for k, v in self.cmd_handlers.items()})  # Include new command handlers
        return "app.cmdHandlers = {" + ",".join(f"'{k}': {v}" for k, v in handlers.items()) + "};"

    @property
    def init_js(self):
        bubble_init_js = "\n".join(bubble.init_js for bubble in self.cmd_bubbles)
        #Generate JavaScript functions for new command handlers
        cmd_handlers_js = "\n".join(f"function {handler.__name__}(payload) {{ {handler(None)} }}" for handler in self.cmd_handlers.values())
        return f"{bubble_init_js}\n{cmd_handlers_js}"

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
        if self.css_framework == CSSFramework.PICO:
            return '<link rel="stylesheet" href="https://unpkg.com/@picocss/pico@1.*/css/pico.min.css">'
        elif self.css_framework == CSSFramework.BOOTSTRAP:
            return '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">'
        elif self.css_framework == CSSFramework.TAILWIND:
            return '<script src="https://cdn.tailwindcss.com"></script>'
        else:
            return ''

    def _get_js_links(self):
        return '\n'.join([f'<script src="{lib}"></script>' for lib in self.js_libraries])

    def _get_js_link(self):
        if self.css_framework == CSSFramework.BOOTSTRAP:
            return '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>'
        else:
            return ''

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="127.0.0.1", port=5001)
