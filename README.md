# Pass Profile Manager

A command-line utility that generates environment variables from profiles stored in the [pass](https://www.passwordstore.org/) password manager.

## Overview

This tool allows you to store environment variables securely in your pass password store and easily load them into your shell environment. It's particularly useful for managing different sets of environment variables for different projects or environments.

Pass Profile Manager supports two ways to define profiles:

1. Directly in your pass password store under `Profile/<profile_name>/`
1. Using aliases in text files in `~/.pass-profile/profile/<profile_name>`

This dual approach gives you flexibility to store sensitive credentials securely in pass while also allowing for easier management of profile compositions through text files.

## Requirements

- [pass](https://www.passwordstore.org/) password manager
- Python 3.6+

## Installation

### Using pipx (recommended)

The easiest way to install Pass Profile Manager is using [pipx](https://pypa.github.io/pipx/), which installs the package in an isolated environment:

```bash
pipx install git+https://github.com/GavinMendelGleason/pass-profile.git
```

After installation, you'll need to set up shell integration as described in the [Shell Integration](#shell-integration) section below.

### Using Nix

#### With nix profile

You can install Pass Profile Manager using the Nix package manager:

```bash
nix profile install github:GavinMendelGleason/pass-profile
```

After installation, you'll need to set up shell integration as described in the [Shell Integration](#shell-integration) section below.

#### With Home Manager

If you use Home Manager, add this to your flake inputs:

```nix
pass-profile = {
  url = "github:GavinMendelGleason/pass-profile";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

Then add the following to your configuration:

```nix
{ pkgs, ... }:

{
  imports = [
    # Import the home-module from the flake
    inputs.pass-profile.homeModules.pass-profile
  ];

  # Enable the module
  programs.pass-profile.enable = true;
}
```

With this Home Manager setup, shell integration is automatically configured for you based on your enabled shells.

For more details on all available options, see the [Home Manager Options](#home-manager-options) section below.

### Shell Integration

For easier usage, you can define a function in your shell configuration file:

#### Bash/Zsh Function

Add this to your `.bashrc` or `.zshrc` file:

```bash
# Load environment variables from pass profile
pass-profile() {
  local profile=${1:-default}
  eval "$(pass-profile-dump-vars $profile)"
  echo "Loaded environment from profile: $profile"
}
```

Then you can simply use:

```bash
pass-profile development
```

This will load all environment variables from the "development" profile, or use "default" if no profile is specified.

#### Fish Function

For Fish shell users, add this to your `~/.config/fish/functions/pass-profile.fish`:

```fish
function pass-profile
  set profile $argv[1]
  if test -z "$profile"
    set profile "default"
  end

  eval (pass-profile-dump-vars $profile)
  echo "Loaded environment from profile: $profile"
end
```

## Usage

```bash
pass-profile-dump-vars [profile_name]
```

Where `profile_name` is the name of the profile stored in pass (under `Profile/`). If not specified, it defaults to "default".

To load the environment variables into your current shell, use:

```bash
eval $(pass-profile-dump-vars [profile_name])
```

## How It Works

1. The tool looks for environment variables from two sources:
   - Your pass password store under `Profile/<profile_name>/`
   - Text files in `~/.pass-profile/profile/<profile_name>`
1. Entries from both sources are merged, with file-based entries taking precedence if duplicates exist
1. The tool outputs shell commands to set these environment variables, which can be evaluated by your shell

## Profile Sources

### Pass Password Store

Entries stored in your pass password store under `Profile/<profile_name>/` are automatically loaded as environment variables. The entry name becomes the environment variable name (uppercased), and its content becomes the value.

### Profile Files

Profile files define aliases to passwords stored in your pass password store. The values in these files are not the passwords themselves, but rather paths that refer to passwords in your password store.

You can define profiles in text files located at `~/.pass-profile/profile/<profile_name>`. Each line in these files can be in one of these formats:

1. **Comments**: Lines starting with `#` are ignored

   ```
   # This is a comment
   ```

1. **Direct password paths**: Just specify a path in your pass store

   ```
   Social/github
   ```

   This will create an environment variable named after the last part of the path (uppercased), e.g., `GITHUB`

1. **Custom variable mapping**: Specify a custom environment variable name and pass path

   ```
   GITHUB_TOKEN:Social/github
   ```

   This will create an environment variable named `GITHUB_TOKEN` with the value from `Social/github`

When both sources define the same environment variable, the file-based definition takes precedence, and a warning is displayed.

## Setting Up Profiles

To set up a profile:

1. Create environment variables in your pass store:

```bash
pass insert Profile/myproject/API_KEY
pass insert Profile/myproject/DATABASE_URL
```

2. Load them into your shell:

```bash
eval $(pass-profile-dump-vars myproject)
```

## Example

Storing environment variables:

```bash
pass insert Profile/development/API_KEY
# Enter your API key when prompted
pass insert Profile/development/DATABASE_URL
# Enter your database URL when prompted
```

Loading the environment variables:

```bash
eval $(pass-profile-dump-vars development)
```

This will set the environment variables `API_KEY` and `DATABASE_URL` in your current shell session.

## Home Manager Options

The Home Manager module provides the following options:

- `programs.pass-profile.enable`: Enable the pass-profile module
- `programs.pass-profile.package`: The pass-profile package to use (defaults to the one from the flake)
- `programs.pass-profile.enableZshIntegration`: Whether to enable Zsh integration (defaults to `true` if Zsh is enabled)
- `programs.pass-profile.enableBashIntegration`: Whether to enable Bash integration (defaults to `true` if Bash is enabled)
- `programs.pass-profile.profile`: An attribute set of profiles, where each profile is an attribute set mapping environment variable names to pass paths

### Profile Configuration

The `programs.pass-profile.profile` option allows you to define profiles directly in your Home Manager configuration:

```nix
programs.pass-profile.profile = {
  default = {
    GITHUB_TOKEN = "Social/github/token";
    NPM_AUTH_TOKEN = "Development/npm/auth_token";
  };
  work = {
    AWS_ACCESS_KEY_ID = "Work/aws/access_key_id";
    AWS_SECRET_ACCESS_KEY = "Work/aws/secret_key";
    SLACK_API_TOKEN = "Work/slack/api_token";
  };
};
```

This will create profile files in `~/.pass-profile/profile/` that can be loaded with:

```bash
pass-profile default
# or
pass-profile development
```

Each entry in a profile maps an environment variable name to a path in your password store. When the profile is loaded, pass-profile will retrieve the values from your password store and set them as environment variables.
