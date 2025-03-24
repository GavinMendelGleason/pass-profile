packages:
{
  config,
  lib,
  pkgs,
  ...
}:

with lib;

let
  cfg = config.programs.pass-profile;
  pass-profile = ''
    pass-profile() {
      local profile=''${1:-default}
      eval "$(pass-profile-dump-vars $profile)"
      echo "Loaded environment from profile: $profile"
    }
  '';
in
{
  options.programs.pass-profile = {
    enable = mkEnableOption "pass-profile - environment variable profile manager";

    package = mkOption {
      type = types.package;
      default = packages.${pkgs.system}.pass-profile;
      description = "The pass-profile package to use.";
    };

    enableZshIntegration = mkOption {
      type = types.bool;
      default = config.programs.zsh.enable;
      description = "Whether to enable pass-profile integration with Zsh.";
    };

    enableBashIntegration = mkOption {
      type = types.bool;
      default = config.programs.bash.enable;
      description = "Whether to enable pass-profile integration with Bash.";
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    programs.zsh.initExtra = mkIf cfg.enableZshIntegration pass-profile;
    programs.bash.initExtra = mkIf cfg.enableBashIntegration pass-profile;
  };
}
