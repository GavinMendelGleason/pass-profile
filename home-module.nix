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

  # Function to write profile files
  writeProfileFile =
    name: vars:
    pkgs.writeTextFile {
      name = name;
      text = concatStringsSep "\n" (mapAttrsToList (envVar: passPath: "${envVar}:${passPath}") vars);
      destination = "/share/pass-profile/profile/${name}";
    };

  # Create a package that contains all the profile files
  profilePackage = pkgs.symlinkJoin {
    name = "pass-profile-profiles";
    paths = mapAttrsToList writeProfileFile cfg.profile;
  };

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

    profile = mkOption {
      type = types.attrsOf (types.attrsOf types.str);
      default = { };
      example = literalExpression ''
        {
          default = {
            GITHUB_TOKEN = "Social/github/token";
            NPM_AUTH_TOKEN = "Development/npm/auth_token";
          };
          work = {
            AWS_ACCESS_KEY_ID = "Work/aws/access_key_id";
            AWS_SECRET_ACCESS_KEY = "Work/aws/secret_key";
            JIRA_API_TOKEN = "Work/jira/api_token";
          };
        }
      '';
      description = ''
        An attribute set of profiles, where each profile is an attribute set
        mapping environment variable names to pass paths.

        These will be written to ~/.pass-profile/profile/ and can be used
        alongside profiles stored in the password store.
      '';
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    # Link the profile files from the profile package
    home.file = mkIf (cfg.profile != { }) {
      "pass-profile/profile".source = "${profilePackage}/share/pass-profile/profile";
      "pass-profile/profile".target = ".pass-profile/profile";
    };

    programs.zsh.initContent = mkIf cfg.enableZshIntegration pass-profile;
    programs.bash.initExtra = mkIf cfg.enableBashIntegration pass-profile;
  };
}
