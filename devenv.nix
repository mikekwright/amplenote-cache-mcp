{ pkgs, project-name, python-pkgs, ... }:

rec {
  # https://devenv.sh/basics/
  env.PROJECT_NAME = project-name;

  # https://devenv.sh/packages/
  packages = [ pkgs.jq ];

  languages.python = {
    enable = true;
    package = python-pkgs.python312;
    poetry = {
      enable = true;
      install = {
        enable = true;
        allExtras = true;
      };
    };
  };

  scripts.helpme = {
    description = "Helpful commands for working with python";
    exec = ''
      echo "Helpme for python"
    '';
  };

  scripts.show-project = {
    description = "Show the project files in a tree view";
    exec = ''
      tree \$DEVENV_ROOT \$@
    '';
  };

  scripts.hints = {
    description = "Show available scripts with descriptions";
    exec = ''
      echo "Available scripts in devenv:"
      ${builtins.concatStringsSep "\n" (
        builtins.map (name:
          let
            script = scripts.${name};
            hasDesc = script ? description;
          in
            if hasDesc
            then "echo \"${name}: ${script.description}\""
            else "echo \"${name}\""
        ) (builtins.attrNames scripts)
      )}
    '';
  };

  scripts.mcp-start = {
    description = "Start the mcp server";
    exec = ''
      python -m app
    '';
  };

  scripts.run-tests = {
    description = "Run the test suite";
    exec = ''
      poetry run pytest
    '';
  };

  scripts.setup-claude-desktop = {
    description = "Setup Claude Desktop MCP server configuration";
    exec = ''
      #!/usr/bin/env bash

      # Determine the Claude config directory based on OS
      if [[ "$OSTYPE" == "darwin"* ]]; then
        CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
      else
        CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
      fi

      CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

      # Get optional DB path argument or use default
      DB_PATH="''${1:-$HOME/.config/ample-electron/amplenote.db}"

      # Create config directory if it doesn't exist
      mkdir -p "$CLAUDE_CONFIG_DIR"

      # Initialize config file if it doesn't exist
      if [ ! -f "$CONFIG_FILE" ]; then
        echo '{"mcpServers":{}}' > "$CONFIG_FILE"
        echo "Created new Claude Desktop config at: $CONFIG_FILE"
      fi

      # Check if jq is available
      if ! command -v jq &> /dev/null; then
        echo "Error: jq is required but not found. Please install jq."
        exit 1
      fi

      # Get current working directory
      CURRENT_DIR="$DEVENV_ROOT"

      # Create the MCP server configuration
      MCP_CONFIG=$(cat <<EOF
      {
        "command": "nix",
        "args": ["develop", "--no-pure-eval", "--command", "mcp-start"],
        "cwd": "$CURRENT_DIR",
        "env": {
          "AMPLENOTE_DB_PATH": "$DB_PATH"
        }
      }
      EOF
      )

      # Check if amplenote server already exists
      if jq -e '.mcpServers.amplenote' "$CONFIG_FILE" > /dev/null 2>&1; then
        echo "Amplenote MCP server already exists in config."
        echo "Current configuration:"
        jq '.mcpServers.amplenote' "$CONFIG_FILE"
        echo ""
        read -p "Do you want to update it? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
          echo "Configuration unchanged."
          exit 0
        fi
      fi

      # Add or update the amplenote MCP server
      TMP_FILE=$(mktemp)
      jq --argjson config "$MCP_CONFIG" '.mcpServers.amplenote = $config' "$CONFIG_FILE" > "$TMP_FILE"
      mv "$TMP_FILE" "$CONFIG_FILE"

      echo "✅ Successfully configured Amplenote MCP server in Claude Desktop!"
      echo ""
      echo "Configuration details:"
      echo "  Config file: $CONFIG_FILE"
      echo "  Database path: $DB_PATH"
      echo "  Working directory: $CURRENT_DIR"
      echo ""
      echo "Please restart Claude Desktop for the changes to take effect."
    '';
  };
}
