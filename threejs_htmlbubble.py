from fasttea import FastTEA, Model, Msg, Cmd, Element, HtmlBubble, CSSFramework
from fasttea.html import div, input_, label
from fasttea.picocss import container, card, grid
from typing import Optional


# Model definition
class CubeModel(Model):
    color: str = "#ff0000"  # Default red color
    rotation_speed: float = 1.0  # Default rotation speed


# Initialize FastTEA app
app = FastTEA(
    initial_model=CubeModel(),
    css_framework=CSSFramework.PICO
)

# Create HTML Bubble for the 3D cube
cube_bubble = app.add_html_bubble(HtmlBubble(
    name="Cube3D",
    js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
    class_definition="""
    class Cube3D extends HTMLElement {
        constructor() {
            super();
            this.attachShadow({ mode: 'open' });

            // Three.js components
            this.scene = null;
            this.camera = null;
            this.renderer = null;
            this.cube = null;
            this.rotationSpeed = 1.0;

            // Create container
            this.container = document.createElement('div');
            this.shadowRoot.appendChild(this.container);
        }

        connectedCallback() {
            const width = parseInt(this.getAttribute('width') || '300');
            const height = parseInt(this.getAttribute('height') || '300');
            this.initThreeJS(width, height);
            this.animate();
        }

        disconnectedCallback() {
            // Cleanup when element is removed
            this.renderer.dispose();
        }

        initThreeJS(width, height) {
            // Setup scene
            this.scene = new THREE.Scene();
            this.camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000);
            this.renderer = new THREE.WebGLRenderer();
            this.renderer.setSize(width, height);
            this.container.appendChild(this.renderer.domElement);

            // Create cube
            const sun = new THREE.DirectionalLight();
            sun.position.set(1,2,3)
            this.scene.add(sun)
        
            const ambient = new THREE.AmbientLight()
            ambient.intensity = 0.5
            this.scene.add(ambient)
        
            const geometry = new THREE.BoxGeometry();
            const material = new THREE.MeshStandardMaterial({ color:  0xff0000 });
            this.cube = new THREE.Mesh(geometry, material);
            this.scene.add(this.cube);

            this.camera.position.z = 5;
        }

        animate() {
            requestAnimationFrame(() => this.animate());

            if (this.cube) {
                this.cube.rotation.x += 0.01 * this.rotationSpeed;
                this.cube.rotation.y += 0.01 * this.rotationSpeed;
            }

            if (this.renderer && this.scene && this.camera) {
                this.renderer.render(this.scene, this.camera);
            }
        }

        setColor(color) {
            if (this.cube) {
                this.cube.material.color.setStyle(color);
            }
        }

        setRotationSpeed(speed) {
            this.rotationSpeed = speed;
        }

        // Observed attributes
        static get observedAttributes() {
            return ['color', 'speed', 'width', 'height'];
        }

        // Attribute change handler
        attributeChangedCallback(name, oldValue, newValue) {
            if (name === 'color') {
                this.setColor(newValue);
            } else if (name === 'speed') {
                this.setRotationSpeed(parseFloat(newValue));
            } else if (name === 'width' || name === 'height') {
                if (this.renderer) {
                    const width = parseInt(this.getAttribute('width') || '300');
                    const height = parseInt(this.getAttribute('height') || '300');
                    this.renderer.setSize(width, height);
                    this.camera.aspect = width / height;
                    this.camera.updateProjectionMatrix();
                }
            }
        }
    }

    // Register the custom element
    customElements.define('three-cube', Cube3D);
    """
))


# Command handlers
@app.cmd("setColor")
def set_color(payload):
    return """
    document.querySelector('three-cube').setColor(payload.color);
    """


@app.cmd("setSpeed")
def set_speed(payload):
    return """
    document.querySelector('three-cube').setRotationSpeed(payload.speed);
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
                # Using the custom element
                div({"class": "cube-container"}, [
                    Element("three-cube", {
                        "color": model.color,
                        "speed": str(model.rotation_speed),
                        "width": "400",
                        "height": "400"
                    }, [])
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