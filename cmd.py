from fastapi import FastAPI
from pydantic import BaseModel
from fasttea import FastTEA, CSSFramework, Element, Msg, Cmd
from fasttea.html import div, input_, button, p

# Model definition
class AppModel(BaseModel):
    name: str = ""
    time: str = ""

# Initialize FastTEA application
app = FastTEA(
    AppModel(),
    css_framework=CSSFramework.PICO,
    debug=True
)

# Update function
@app.update
def update(msg: Msg, model: AppModel) -> tuple[AppModel, Cmd | None]:
    match msg.action:
        case "change_name":
            new_model = AppModel(name=msg.value, time=model.time)
            if new_model.name and new_model.time:
                return new_model, Cmd(action="show_message", payload={
                    "message": f"Name: {new_model.name}, Time: {new_model.time}"
                })
            return new_model, None
        case "new_time":
            return model, Cmd(action="get_time")
        case "set_time":
            return AppModel(name=model.name, time=msg.value), None
    return model, None

# View function
@app.view
def view(model: AppModel) -> Element:
    return div({}, [
        div({}, [
            input_({
                "type": "text",
                "placeholder": "Enter name",
                "value": model.name,
                "id": "name-input"
            }, ""),
            button({
                "onClick": "change_name",
                "getValue": "name-input"
            }, "Change Name"),
            button({
                "onClick": "new_time"
            }, "Aktuelle Uhrzeit"),
        ]),
        p({}, f"Name: {model.name}"),
        p({}, f"Time: {model.time}")
    ])

# Command handlers for browser
@app.cmd("get_time")
def get_time(payload=None) -> str:
    """Returns JavaScript that uses auto-messaging to send time back to server"""
    return """
    const now = new Date();
    const time = now.toLocaleTimeString();
    return {
        msg: {
            action: 'set_time',
            value: time
        }
    };
    """

@app.cmd("show_message")
def show_message(payload=None) -> str:
    return """
    window.alert(payload.message);
    return null;  // No message to send back
    """

if __name__ == "__main__":
    app.run()