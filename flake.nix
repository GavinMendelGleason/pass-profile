{
  description = "pass-profile";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:nixOS/nixpkgs?ref=nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    inputs@{ self, flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.treefmt-nix.flakeModule
      ];
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      perSystem =
        {
          pkgs,
          self',
          ...
        }:
        {
          treefmt = {
            programs = {
              nixfmt.enable = true;
              black.enable = true;
              mdformat.enable = true;
              taplo.enable = true;
            };
            settings = {
              global.excludes = [
                ".envrc"
                ".python-version"
              ];
            };
          };

          # NOTE: this setup is only going to work as long as pass-profile is just a single python script.
          # The moment this gets a little more complex it might be better to switch to uvpart.
          packages = rec {
            default = pass-profile;
            pass-profile = pkgs.writeShellApplication {
              name = "pass-profile";
              runtimeInputs = [ pkgs.pass ];
              text = ''exec ${pkgs.python3}/bin/python ${./pass_profile/main.py} "$@"'';
            };
          };
        };
      flake = {
        homeModules = {
          pass-profile = import ./home-module.nix self.packages;
        };
      };
    };
}
