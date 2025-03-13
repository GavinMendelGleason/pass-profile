import argparse
import subprocess
import sys
import os


def get_pass_entries(profile_name):
    """Get all entries under the given profile from pass."""
    try:
        # List all entries under Profile/{profile_name}
        cmd = ["pass", "ls", f"Profile/{profile_name}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the output to get entry names
        entries = []
        result_list = result.stdout.strip().split('\n')
        if len(result_list) > 1:
            result_list = result_list[1:]

        for line in result_list:
            # Skip the first line which is the directory name and empty lines
            if line and not line.endswith('/'):
                # Extract just the env var name (last part of the path)
                entry = line.strip().strip('└──').strip('├──').strip()
                if '/' in entry:
                    entry = entry.split('/')[-1]
                if entry:
                    entries.append(entry)

        return entries
    except subprocess.CalledProcessError as e:
        print(f"Error accessing pass: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_env_value(profile_name, env_var):
    """Get the value of an environment variable from pass."""
    try:
        cmd = ["pass", f"Profile/{profile_name}/{env_var}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving {env_var}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='Generate environment variables from pass profiles.')
    parser.add_argument('profile_name', nargs='?', default='default',
                        help='Name of the profile in pass (stored under Profile/). Defaults to "default"')

    args = parser.parse_args()

    # Get all environment variables stored in the profile
    env_vars = get_pass_entries(args.profile_name)

    if not env_vars:
        print(f"No environment variables found for profile '{args.profile_name}'", file=sys.stderr)
        sys.exit(1)

    # Generate shell commands to set environment variables
    for env_var in env_vars:
        value = get_env_value(args.profile_name, env_var)
        if value:
            # Escape special characters in the value
            escaped_value = value.replace('"', '\\"')
            print(f'export {env_var}="{escaped_value}"')


if __name__ == "__main__":
    main()
