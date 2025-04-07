import argparse
import subprocess
import sys
import os
import pathlib


def get_pass_entries(profile_name):
    """Get all entries under the given profile from pass."""
    try:
        # List all entries under Profile/{profile_name}
        cmd = ["pass", "ls", f"Profile/{profile_name}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the output to get entry names
        entries = {}
        result_list = result.stdout.strip().split("\n")
        if len(result_list) > 1:
            result_list = result_list[1:]

        for line in result_list:
            # Skip the first line which is the directory name and empty lines
            if line and not line.endswith("/"):
                # Extract just the env var name (last part of the path)
                entry = line.strip().strip("└──").strip("├──").strip()
                if "/" in entry:
                    entry = entry.split("/")[-1]
                if entry:
                    # Add to dictionary with env_var_name as key (uppercased) and pass_path as value
                    entries[entry.upper()] = f"Profile/{profile_name}/{entry}"

        return entries
    except subprocess.CalledProcessError as e:
        # Check if this is just a "not in password store" error
        if "is not in the password store" in e.stderr:
            return None
        # For other errors, exit with error
        print(f"Error accessing pass: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_file_entries(profile_name):
    """Get all entries from a .pass-profile/profile/{profile_name} file."""
    entries = {}
    profile_path = pathlib.Path.home() / ".pass-profile" / "profile" / profile_name

    if not profile_path.exists():
        return None

    try:
        with open(profile_path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Check if it's in the format name:password
                if ":" in line:
                    env_var, pass_path = line.split(":", 1)
                    entries[env_var.strip()] = pass_path.strip()
                else:
                    # It's just a password path, extract the last part as env var name
                    pass_path = line
                    env_var = pass_path.split("/")[-1].upper()
                    entries[env_var] = pass_path
        return entries
    except Exception as e:
        print(f"Error reading profile file {profile_path}: {e}", file=sys.stderr)
        sys.exit(1)


def get_env_value(pass_path):
    """Get the value of an environment variable from pass.

    pass_path is the path to the password in the pass store
    """
    try:
        cmd = ["pass", pass_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving {pass_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate environment variables from pass profiles."
    )
    parser.add_argument(
        "profile_name",
        nargs="?",
        default="default",
        help='Name of the profile in pass (stored under Profile/) or in .pass-profile/profile/. Defaults to "default"',
    )

    args = parser.parse_args()

    # Get environment variables from both sources
    pass_entries = get_pass_entries(args.profile_name)
    file_entries = get_file_entries(args.profile_name)

    # Check if both sources are None (profile doesn't exist in either place)
    if pass_entries is None and file_entries is None:
        print(
            f"Profile '{args.profile_name}' not found in pass store or in .pass-profile/profile/",
            file=sys.stderr,
        )
        sys.exit(1)

    # Initialize env_vars_dict from pass entries
    env_vars_dict = {}
    if pass_entries is not None:
        env_vars_dict.update(pass_entries)

    # Add file entries if they exist, overriding any duplicates
    if file_entries is not None:
        # Check for duplicates before updating
        for env_var_name in file_entries:
            if env_var_name in env_vars_dict:
                print(
                    f"Warning: Entry '{env_var_name}' exists in both pass and file profile. Using file version.",
                    file=sys.stderr,
                )

        # Update with file entries
        env_vars_dict.update(file_entries)

    if not env_vars_dict:
        print(
            f"Warning: No environment variables found for profile '{args.profile_name}'",
            file=sys.stderr,
        )
        # Not exiting with error, just warning

    # Generate shell commands to set environment variables
    for env_var_name, pass_path in env_vars_dict.items():
        value = get_env_value(pass_path)
        if value:
            # Escape special characters in the value
            escaped_value = value.replace('"', '\\"')
            print(f'export {env_var_name}="{escaped_value}"')


if __name__ == "__main__":
    main()
