packages:
{
  config,
  lib,
  pkgs,
  ...
}:

with lib;

let
  cfg = config.programs.envprof;
  passenv = ''
    passenv() {
      local profile=''${1:-default}
      eval "$(pass-profile $profile)"
      echo "Loaded environment from profile: $profile"
    }
  '';
in
{
  options.programs.envprof = {
    enable = mkEnableOption "envprof - environment variable profile manager";

    package = mkOption {
      type = types.package;
      default = packages.${pkgs.system}.envprof;
      description = "The envprof package to use.";
    };

    enableZshIntegration = mkOption {
      type = types.bool;
      default = config.programs.zsh.enable;
      description = "Whether to enable envprof integration with Zsh.";
    };

    enableBashIntegration = mkOption {
      type = types.bool;
      default = config.programs.bash.enable;
      description = "Whether to enable envprof integration with Bash.";
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    programs.zsh.initExtra = mkIf cfg.enableZshIntegration passenv;
    programs.bash.initExtra = mkIf cfg.enableBashIntegration passenv;
  };
}
