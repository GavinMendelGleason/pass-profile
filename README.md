# Pass Profile Manager

A command-line utility that generates environment variables from profiles stored in the [pass](https://www.passwordstore.org/) password manager.

## Overview

This tool allows you to store environment variables securely in your pass password store and easily load them into your shell environment. It's particularly useful for managing different sets of environment variables for different projects or environments.

## Requirements

- [pass](https://www.passwordstore.org/) password manager
- Python 3.6+

## Installation

### Using pipx (recommended)

The easiest way to install Pass Profile Manager is using [pipx](https://pypa.github.io/pipx/), which installs the package in an isolated environment:

```bash
pipx install git+https://github.com/GavinMendelGleason/pass-profile.git
```

### Using Nix

#### With nix profile

You can install Pass Profile Manager using the Nix package manager:

```bash
nix profile install github:GavinMendelGleason/pass-profile
```

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

1. The tool looks for environment variables stored in your pass password store under `Profile/<profile_name>/`.
1. Each entry under this path is treated as an environment variable, with the entry name as the variable name and its content as the value.
1. The tool outputs shell commands to set these environment variables, which can be evaluated by your shell.

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

## Security Notes

- Environment variables are stored securely in your pass password store, which is encrypted with GPG.
- The tool only outputs the commands to set environment variables; it doesn't store them anywhere else.
- Be cautious when using `eval` with any command that produces output from external sources.

## Shell Integration

### Shell Integration

#### Bash/Zsh Function

For easier usage, you can define a function in your `.bashrc` or `.zshrc` file:

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
