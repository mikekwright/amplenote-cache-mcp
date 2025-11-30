{
  description = "Flake to setup devenv for python development";

  inputs = {
    # Python version 3.11.14 (~Oct 10th, 2025)
    python-target.url = "github:nixos/nixpkgs/870493f9a8cb0b074ae5b411b2f232015db19a65";

    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    devenv.url = "github:cachix/devenv";
    flake-parts.url = "github:hercules-ci/flake-parts";

    # This is the devenv support
    nixpkgs-python = {
      url = "github:cachix/nixpkgs-python";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ self, nixpkgs, flake-parts, devenv, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [ devenv.flakeModule ];

      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];

      perSystem = { system, pkgs, ... }: 
        let
          python-pkgs = import inputs.python-target { inherit system; };
          project-name = "python-project";
        in
        {
          devenv.shells.default = {
            _module.args = { inherit python-pkgs project-name; };
            imports = [ ./devenv.nix ];
          };
      };
    };
}

