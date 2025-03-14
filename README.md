# Pass Profile Manager

A command-line utility that generates environment variables from profiles stored in the [pass](https://www.passwordstore.org/) password manager.

## Overview

This tool allows you to store environment variables securely in your pass password store and easily load them into your shell environment. It's particularly useful for managing different sets of environment variables for different projects or environments.

## Requirements

- [pass](https://www.passwordstore.org/) password manager
- Python 3.6+

## Installation

Clone this repository and ensure the script is executable:

```bash
git clone <repository-url>
cd <repository-directory>
chmod +x main.py
```

You may want to create a symlink to the script in a directory that's in your PATH:

```bash
ln -s $(pwd)/main.py ~/.local/bin/pass-profile
```

## Usage

```bash
python main.py [profile_name]
```

Where `profile_name` is the name of the profile stored in pass (under `Profile/`). If not specified, it defaults to "default".

To load the environment variables into your current shell, use:

```bash
eval $(python main.py [profile_name])
```

## How It Works

1. The tool looks for environment variables stored in your pass password store under `Profile/<profile_name>/`.
2. Each entry under this path is treated as an environment variable, with the entry name as the variable name and its content as the value.
3. The tool outputs shell commands to set these environment variables, which can be evaluated by your shell.

## Setting Up Profiles

To set up a profile:

1. Create environment variables in your pass store:

```bash
pass insert Profile/myproject/API_KEY
pass insert Profile/myproject/DATABASE_URL
```

2. Load them into your shell:

```bash
eval $(python main.py myproject)
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
eval $(python main.py development)
```

This will set the environment variables `API_KEY` and `DATABASE_URL` in your current shell session.

## Security Notes

- Environment variables are stored securely in your pass password store, which is encrypted with GPG.
- The tool only outputs the commands to set environment variables; it doesn't store them anywhere else.
- Be cautious when using `eval` with any command that produces output from external sources.

## Shell Integration

### Zsh Function

For easier usage, you can define a function in your `.zshrc` file:

```zsh
# Load environment variables from pass profile
passenv() {
  local profile=${1:-default}
  eval "$(python /path/to/main.py $profile)"
  echo "Loaded environment from profile: $profile"
}
```

Then you can simply use:

```bash
passenv development
```

This will load all environment variables from the "development" profile, or use "default" if no profile is specified.
