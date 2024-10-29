from typing import Dict, Any, Union, List

from fasttea import HtmlBubble, FastTEA, Element


class Scene3DBubble(HtmlBubble):
    def __init__(self):
        super().__init__(name="3DScene",
                         js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
                         class_definition="""
                         class Scene3D extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      
      // Three.js Komponenten
      this.scene = null;
      this.activeCamera = null;
      this.renderer = null;
      this.objects = new Map();
      
      // Styles für das Canvas
      const style = document.createElement('style');
      style.textContent = `
        :host {
          display: block;
          width: 100%;
          height: 100%;
        }
        canvas {
          width: 100%;
          height: 100%;
        }
      `;
      this.shadowRoot.appendChild(style);
    }
  
    connectedCallback() {
      this.initScene();
      this.setupResizeHandler();
      this.animate();
    }
  
    disconnectedCallback() {
      window.removeEventListener('resize', this.handleResize);
      this.renderer?.dispose();
    }
  
    initScene() {
      // Scene erstellen
      this.scene = new THREE.Scene();
      
      // Renderer erstellen
      this.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.renderer.setSize(this.clientWidth, this.clientHeight);
      this.shadowRoot.appendChild(this.renderer.domElement);
    }
  
    setupResizeHandler() {
      this.handleResize = () => {
        if (this.activeCamera) {
          this.activeCamera.aspect = this.clientWidth / this.clientHeight;
          this.activeCamera.updateProjectionMatrix();
        }
        this.renderer.setSize(this.clientWidth, this.clientHeight);
      };
      window.addEventListener('resize', this.handleResize);
    }
  
    animate() {
      requestAnimationFrame(() => this.animate());
      this.objects.forEach(obj => {
        if (obj.userData.animate) {
          obj.rotation.x += 0.01;
          obj.rotation.y += 0.01;
        }
      });
      if (this.activeCamera) {
        this.renderer.render(this.scene, this.activeCamera);
      }
    }
  
    // API für Child-Elemente
    addObject(id, object, options = {}) {
      object.userData = { ...object.userData, ...options };
      this.objects.set(id, object);
      this.scene.add(object);
    }
  
    removeObject(id) {
      const object = this.objects.get(id);
      if (object) {
        this.scene.remove(object);
        this.objects.delete(id);
      }
    }
  
    setActiveCamera(camera) {
      this.activeCamera = camera;
      if (camera) {
        camera.aspect = this.clientWidth / this.clientHeight;
        camera.updateProjectionMatrix();
      }
    }
  }
  
  class Scene3DObject extends HTMLElement {
    static get observedAttributes() {
      return ['position-x', 'position-y', 'position-z', 'rotation-x', 'rotation-y', 'rotation-z'];
    }
  
    constructor() {
      super();
      this.object3D = null;
    }
  
    connectedCallback() {
      this.createObject();
    }
  
    disconnectedCallback() {
      const scene = this.closest('scene-3d');
      if (scene && this.id) {
        scene.removeObject(this.id);
      }
    }
  
    attributeChangedCallback(name, oldValue, newValue) {
      if (!this.object3D) return;
  
      const value = parseFloat(newValue) || 0;
      switch (name) {
        case 'position-x': this.object3D.position.x = value; break;
        case 'position-y': this.object3D.position.y = value; break;
        case 'position-z': this.object3D.position.z = value; break;
        case 'rotation-x': this.object3D.rotation.x = THREE.MathUtils.degToRad(value); break;
        case 'rotation-y': this.object3D.rotation.y = THREE.MathUtils.degToRad(value); break;
        case 'rotation-z': this.object3D.rotation.z = THREE.MathUtils.degToRad(value); break;
      }
    }
  
    createObject() {
      // Wird von Kindklassen überschrieben
    }
  
    updatePosition() {
      if (!this.object3D) return;
      
      this.object3D.position.set(
        parseFloat(this.getAttribute('position-x')) || 0,
        parseFloat(this.getAttribute('position-y')) || 0,
        parseFloat(this.getAttribute('position-z')) || 0
      );
    }
  
    updateRotation() {
      if (!this.object3D) return;
      
      this.object3D.rotation.set(
        THREE.MathUtils.degToRad(parseFloat(this.getAttribute('rotation-x')) || 0),
        THREE.MathUtils.degToRad(parseFloat(this.getAttribute('rotation-y')) || 0),
        THREE.MathUtils.degToRad(parseFloat(this.getAttribute('rotation-z')) || 0)
      );
    }
  }
  
    customElements.define('scene-3d', Scene3D);
    
                         """)

class CameraBubble(HtmlBubble):
    def __init__(self):
        super().__init__(name="Camera",
                         js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
                         class_definition="""
class Scene3DCamera extends Scene3DObject {
    static get observedAttributes() {
      return [
        ...super.observedAttributes,
        'fov',
        'near',
        'far',
        'active'
      ];
    }
  
    createObject() {
      const fov = parseFloat(this.getAttribute('fov')) || 75;
      const near = parseFloat(this.getAttribute('near')) || 0.1;
      const far = parseFloat(this.getAttribute('far')) || 1000;
      
      this.object3D = new THREE.PerspectiveCamera(fov, 1, near, far);
      this.updatePosition();
      this.updateRotation();
      
      const scene = this.closest('scene-3d');
      if (scene && this.id) {
        scene.addObject(this.id, this.object3D);
        if (this.hasAttribute('active')) {
          scene.setActiveCamera(this.object3D);
        }
      }
    }
  
    attributeChangedCallback(name, oldValue, newValue) {
      super.attributeChangedCallback(name, oldValue, newValue);
      
      if (!this.object3D) return;
  
      switch (name) {
        case 'fov':
          this.object3D.fov = parseFloat(newValue) || 75;
          this.object3D.updateProjectionMatrix();
          break;
        case 'near':
          this.object3D.near = parseFloat(newValue) || 0.1;
          this.object3D.updateProjectionMatrix();
          break;
        case 'far':
          this.object3D.far = parseFloat(newValue) || 1000;
          this.object3D.updateProjectionMatrix();
          break;
        case 'active':
          const scene = this.closest('scene-3d');
          if (scene) {
            scene.setActiveCamera(newValue !== null ? this.object3D : null);
          }
          break;
      }
    }
  }
  
  customElements.define('scene-3d-camera', Scene3DCamera);
                         """)

class DirectionalLight(HtmlBubble):
    def __init__(self):
        super().__init__(name="DirectionalLight",
                         js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
                         class_definition="""
                         
class Scene3DDirectionalLight extends Scene3DObject {
    static get observedAttributes() {
      return [
        ...super.observedAttributes,
        'color',
        'intensity'
      ];
    }
  
    createObject() {
      const color = this.getAttribute('color') || '#ffffff';
      const intensity = parseFloat(this.getAttribute('intensity')) || 1;
      
      this.object3D = new THREE.DirectionalLight(color, intensity);
      this.updatePosition();
      this.updateRotation();
      
      const scene = this.closest('scene-3d');
      if (scene && this.id) {
        scene.addObject(this.id, this.object3D);
      }
    }
  
    attributeChangedCallback(name, oldValue, newValue) {
      super.attributeChangedCallback(name, oldValue, newValue);
      
      if (!this.object3D) return;
  
      switch (name) {
        case 'color':
          this.object3D.color.set(newValue || '#ffffff');
          break;
        case 'intensity':
          this.object3D.intensity = parseFloat(newValue) || 1;
          break;
      }
    }
  }
  
  customElements.define('scene-3d-directional-light', Scene3DDirectionalLight);
                         """)

class AmbientLight(HtmlBubble):
    def __init__(self):
        super().__init__(name="AmbientLight",
                         js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
                         class_definition="""
class Scene3DAmbientLight extends Scene3DObject {
    static get observedAttributes() {
      return [
        ...super.observedAttributes,
        'color',
        'intensity'
      ];
    }
  
    createObject() {
      const color = this.getAttribute('color') || '#ffffff';
      const intensity = parseFloat(this.getAttribute('intensity')) || 1;
      
      this.object3D = new THREE.AmbientLight(color, intensity);
      
      const scene = this.closest('scene-3d');
      if (scene && this.id) {
        scene.addObject(this.id, this.object3D);
      }
    }
  
    attributeChangedCallback(name, oldValue, newValue) {
      super.attributeChangedCallback(name, oldValue, newValue);
      
      if (!this.object3D) return;
  
      switch (name) {
        case 'color':
          this.object3D.color.set(newValue || '#ffffff');
          break;
        case 'intensity':
          this.object3D.intensity = parseFloat(newValue) || 1;
          break;
      }
    }
  }
  
    customElements.define('scene-3d-ambient-light', Scene3DAmbientLight);
                         """)

class Scene3DCube(HtmlBubble):
    def __init__(self):
        super().__init__(name="Scene3DCube",
                         js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
                         class_definition="""
class Scene3DCube extends Scene3DObject {
    static get observedAttributes() {
      return [
        ...super.observedAttributes,
        'width',
        'height',
        'depth',
        'color'
      ];
    }
  
    createObject() {
      const width = parseFloat(this.getAttribute('width')) || 1;
      const height = parseFloat(this.getAttribute('height')) || 1;
      const depth = parseFloat(this.getAttribute('depth')) || 1;
      
      const geometry = new THREE.BoxGeometry(width, height, depth);
      const material = new THREE.MeshPhongMaterial({
        color: this.getAttribute('color') || 0x00ff00
      });
      
      this.object3D = new THREE.Mesh(geometry, material);
      this.updatePosition();
      this.updateRotation();
      
      const scene = this.closest('scene-3d');
      if (scene && this.id) {
        scene.addObject(this.id, this.object3D, {
          animate: this.hasAttribute('animate')
        });
      }
    }
  
    attributeChangedCallback(name, oldValue, newValue) {
      super.attributeChangedCallback(name, oldValue, newValue);
      
      if (!this.object3D) return;
  
      if (['width', 'height', 'depth'].includes(name)) {
        const width = parseFloat(this.getAttribute('width')) || 1;
        const height = parseFloat(this.getAttribute('height')) || 1;
        const depth = parseFloat(this.getAttribute('depth')) || 1;
        
        this.object3D.geometry.dispose();
        this.object3D.geometry = new THREE.BoxGeometry(width, height, depth);
      }
      
      if (name === 'color') {
        this.object3D.material.color.set(newValue || 0x00ff00);
      }
    }
  }
  
    customElements.define('scene-3d-cube', Scene3DCube);
                         """)

class Scene3DSphere(HtmlBubble):
    def __init__(self):
        super().__init__(name="Scene3DSphere",
                         js_libraries=["https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"],
                         class_definition="""
class Scene3DSphere extends Scene3DObject {
    static get observedAttributes() {
      return [...super.observedAttributes, 'radius', 'color'];
    }
  
    createObject() {
      const geometry = new THREE.SphereGeometry(
        parseFloat(this.getAttribute('radius')) || 1,
        32,
        32
      );
      const material = new THREE.MeshPhongMaterial({
        color: this.getAttribute('color') || 0xff0000
      });
      this.object3D = new THREE.Mesh(geometry, material);
      this.updatePosition();
      this.updateRotation();
      
      const scene = this.closest('scene-3d');
      if (scene && this.id) {
        scene.addObject(this.id, this.object3D, {
          animate: this.hasAttribute('animate')
        });
      }
    }
  
    attributeChangedCallback(name, oldValue, newValue) {
      super.attributeChangedCallback(name, oldValue, newValue);
      
      if (!this.object3D) return;
  
      if (name === 'radius') {
        const radius = parseFloat(newValue) || 1;
        this.object3D.geometry.dispose();
        this.object3D.geometry = new THREE.SphereGeometry(radius, 32, 32);
      }
      
      if (name === 'color') {
        this.object3D.material.color.set(newValue || 0xff0000);
      }
    }
  }
  
    customElements.define('scene-3d-sphere', Scene3DSphere);
                         """)

def scene_3d(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("scene-3d", attributes, children)

def scene_3d_camera(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("scene-3d-camera", attributes, children)

def scene_3d_directional_light(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("scene-3d-directional-light", attributes, children)

def scene_3d_ambient_light(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("scene-3d-ambient-light", attributes, children)

def scene_3d_cube(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("scene-3d-cube", attributes, children)

def scene_3d_sphere(attributes: Dict[str, Any], children: Union[List[Element], Element, str]) -> Element:
    return Element("scene-3d-sphere", attributes, children)

def add_all_bubbles(app:FastTEA)->None:
    app.add_html_bubble(Scene3DBubble())
    app.add_html_bubble(CameraBubble())
    app.add_html_bubble(DirectionalLight())
    app.add_html_bubble(AmbientLight())
    app.add_html_bubble(Scene3DCube())
    app.add_html_bubble(Scene3DSphere())