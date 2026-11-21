
from fastapi import FastAPI

app = FastAPI()


@app.get("/multiply")
def multiply(x: int, y: int):
    return {"result": x * y}

@app.get("/divide")
def divide(x: int, y: int):
    return {"result": x / y}


@app.get("/utcp")
def utcp_manual():
    return {
        "manual_version": "1.0.0",
        "utcp_version": "1.0.1",
        "tools": [
            {
                "name": "multiply",
                "description": "Multiply two integers",
                "inputs": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"}
                    },
                    "required": ["x", "y"]
                },
                "outputs": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "integer"}
                    }
                },
                "tool_call_template": {
                    "call_template_type": "http",
                    "url": "http://127.0.0.1:8000/multiply",
                    "http_method": "GET"
                }
            },
            {
                "name": "divide",
                "description": "Divide two integers",
                "inputs": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"}
                    },
                    "required": ["x", "y"]
                },
                "outputs": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "integer"}
                    }
                },
                "tool_call_template": {
                    "call_template_type": "http",
                    "url": "http://127.0.0.1:8000/divide",
                    "http_method": "GET"
                }
            }
        ]
    }
