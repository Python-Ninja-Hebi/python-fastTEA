from fasttea import FastTEA, Model, Msg, Cmd, Element, CSSFramework
from fasttea.html import div, h1, input_, button, p


class AppModel(Model):
    name: str = ""
    greeting: str = ""

app = FastTEA(AppModel(), css_framework=CSSFramework.PICO)

@app.update
def update(msg: Msg, model: AppModel) -> tuple[AppModel, Cmd | None]:
    if msg.action == "greet":
        model.name = msg.value
        model.greeting = f"Hello {msg.value}!"
    return model, None

@app.view
def view(model: AppModel) -> Element:
    return div({},[
        h1({}, "FastTEA Hello Example"),
        input_({
                "id": "input",
                "type": "text",
                "value": model.name,
                "name": "name",
                "placeholder": "Enter your name"
        }, ""),
        button({
                "onClick": "greet",
                "getValue": "input"
        },"Greet"),
        p ({}, model.greeting)
    ])

app.run()