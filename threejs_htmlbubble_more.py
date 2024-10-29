from fasttea import FastTEA, Model, Msg, Cmd, Element, HtmlBubble, CSSFramework
from fasttea.html import div, input_, label
from fasttea.picocss import container, card, grid
from typing import Optional
from bubbles_3d import scene_3d, scene_3d_camera, scene_3d_directional_light,scene_3d_ambient_light,scene_3d_cube,scene_3d_sphere
import bubbles_3d


# Model definition
class CubeModel(Model):
    color: str = "#ff0000"  # Default red color
    rotation_speed: float = 1.0  # Default rotation speed


# Initialize FastTEA app
app = FastTEA(
    initial_model=CubeModel(),
    css_framework=CSSFramework.PICO
)

bubbles_3d.add_all_bubbles(app)

# Command handlers
@app.cmd("setColor")
def set_color(payload):
    return """
    document.querySelector('cube1').setColor(payload.color);
    """


@app.cmd("setSpeed")
def set_speed(payload):
    return """
    document.querySelector('cube1').setRotationSpeed(payload.speed);
    """


# Update function
@app.update
def update(msg: Msg, model: CubeModel) -> tuple[CubeModel, Optional[Cmd]]:
    if msg.action == "changeColor":
        new_model = CubeModel(
            color=msg.value,
            rotation_speed=model.rotation_speed
        )
        return new_model, Cmd(action="setColor", payload={"color": msg.value})

    elif msg.action == "changeSpeed":
        speed = float(msg.value)
        new_model = CubeModel(
            color=model.color,
            rotation_speed=speed
        )
        return new_model, Cmd(action="setSpeed", payload={"speed": speed})

    return model, None


# View function
@app.view
def view(model: CubeModel) -> Element:
    return container({}, [
        grid({}, [
            # Cube card
            card({}, [
                scene_3d({"style":"width: 600px; height: 400px;"},[
                    scene_3d_camera({
                        "id":"main-camera",
                        "position-z":"5",
                        "fov":"75",
                        "near":"0.1",
                        "far":"1000",
                        "active":"true"
                    },[]),
                    scene_3d_directional_light({
                        "id": "main-light",
                        "color" : "#ffffff",
                        "intensity" : "1",
                        "position-x" : "5",
                        "position-y" : "5",
                        "position-z" : "5"
                    },[]),
                    scene_3d_ambient_light({
                        "id":"ambient",
                        "color" : "#404040",
                        "intensity" : "0.5"
                    },[]),
                    scene_3d_cube({
                        "id":"cube1",
                        "color" : model.color,
                        "width" : "2",
                        "height" : "1",
                        "depth" : "1.5",
                        "position-x" : "1",
                        "position-y" : "0.5",
                        "position-z" : "-1",
                        "rotation-y" : "45",
                        "animate" : "true"
                    },[]),
                    scene_3d_sphere({
                        "id":"sphere1",
                        "color" : "#ff0000",
                        "radius" : "0.5",
                        "position-x" : "-1"
                    },[])
                ])
            ]),
            # Controls card
            card({}, [
                div({}, [
                    label({"for": "colorPicker"}, "Cube Color:"),
                    input_({
                        "type": "color",
                        "id": "colorPicker",
                        "value": model.color,
                        "onChange": "changeColor"
                    }, [])
                ]),
                div({"style": "margin-top: 1rem;"}, [
                    label({"for": "speedSlider"}, f"Rotation Speed ({model.rotation_speed}x):"),
                    input_({
                        "type": "range",
                        "id": "speedSlider",
                        "min": "0",
                        "max": "3",
                        "step": "0.1",
                        "value": str(model.rotation_speed),
                        "onChange": "changeSpeed"
                    }, [])
                ])
            ])
        ])
    ])



app.run()