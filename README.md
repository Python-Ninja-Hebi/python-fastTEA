# fastTEA: Build Elegant Web Applications in Python

fastTEA is a powerful and intuitive Python framework for building web applications with ease. 
Inspired by The Elm Architecture (TEA), fastTEA brings simplicity and predictability to your Python web development workflow.

![](./images/fasttea_small.png)

## Features

- **Simple and Intuitive**: Build web apps using a clear, archtectural approach.
- **Based on The Elm Architecture**: Benefit from a time-tested, scalable architecture.
- **FastAPI Backend**: Leverage the speed and simplicity of FastAPI.
- **HTMX Integration**: Create dynamic UIs without writing JavaScript.
- **Flexible CSS Framework Support**: Choose from Pico, Bootstrap, or Tailwind CSS.
- **Type Safety**: Utilizes Pydantic for robust data validation.

## Installation

Install fastTEA using pip:

```bash
pip install fasttea-web
```

## Quick Start

Let's dive into a simple "Hello, World!" application to showcase the power and simplicity of fastTEA.

```python
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
    return div({},
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
    )

if __name__ == "__main__":
    app.run()
```

![](./images/img1.png)

## Core Principles Explained

1. **Model**: The `AppModel` class defines the application's state. In this example, it stores the user's name and the greeting message.

2. **Update**: The `update` function handles state changes based on messages. It takes the current model and a message, then returns the updated model and any commands to be executed.

3. **View**: The `view` function renders the UI based on the current model state. It returns a tree of `Element` objects that fastTEA converts to HTML.

4. **HTMX Integration**: fastTEA leverages HTMX for dynamic updates without writing JavaScript. The button in our example uses HTMX attributes to trigger a server request.

5. **CSS Framework**: fastTEA supports various CSS frameworks. In this example, we're using Pico CSS for a clean, minimal design.

![](./images/tea.png)

## Get Started Today!

fastTEA combines the best of Python, The Elm Architecture, and modern web technologies to provide a delightful development experience. Whether you're building a small prototype or a large-scale web application, fastTEA has you covered.

Start building your next web application with fastTEA and experience the joy of functional web development in Python!

## More

**FastTEA: A Python Developer's Quest for Elegant Web Apps - Part 1**
https://medium.com/@hebi_73682/fasttea-a-python-developers-quest-for-elegant-web-apps-part-1-ef86461cbfc5

**FastTEA: A Python Developer's Quest for Elegant Web Apps - Part 2**
https://medium.com/@hebi_73682/fasttea-a-python-developers-quest-for-elegant-web-apps-part-2-a25fc77e09c3

### Coming Soon!

We're constantly working to improve fastTEA and add new features. Here's a sneak peek at what's coming:

1. **More Examples**: We're developing a variety of examples to showcase fastTEA's capabilities in different scenarios.

2. **Simple Chatbot**: A demonstration of how to implement a basic chatbot using fastTEA, showing off its real-time update capabilities.

3. **Form Processing**: Enhanced support for handling and processing form submissions, making it even easier to create data-entry applications.

4. **Client-Side Commands**: Introducing a way to define commands that can be executed locally in the browser, improving responsiveness and reducing server load for certain operations.

5. **Server-Triggered Commands**: Allowing the server to trigger these client-side commands, enabling more complex interactions between the server and client.

6. **UiBubbles and CmdBubbles**: More structure.

These upcoming features will make fastTEA even more powerful and flexible, opening up new possibilities for your web applications. Stay tuned for updates!

Happy coding with fastTEA! 🍵✨