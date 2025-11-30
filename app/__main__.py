from .container import Container
from .mcp_app import MCPApp


if __name__ == "__main__":
    container = Container()
    app = container.mcp_app()
    app.run()
