#!/bin/sh

cd $(dirname $0)

nix develop --no-pure-eval --command mcp-start
