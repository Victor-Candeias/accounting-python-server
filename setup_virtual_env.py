import os
import subprocess
import sys

def create_virtual_env(env_name="env"):
    """
    Creates a virtual environment with the specified name.
    """
    print(f"Creating virtual environment: {env_name}")
    subprocess.check_call([sys.executable, "-m", "venv", env_name])
    print(f"Virtual environment '{env_name}' created successfully.")

def activate_virtual_env(env_name="env"):
    """
    Activates the virtual environment (prints activation instructions).
    """
    if os.name == "nt":  # Windows
        activate_path = os.path.join(env_name, "Scripts", "activate")
    else:  # macOS/Linux
        activate_path = os.path.join(env_name, "bin", "activate")

    print(f"To activate the environment, run:\nsource {activate_path}")

def install_dependencies(env_name="env", requirements_file="requirements.txt"):
    """
    Installs dependencies from requirements.txt if the file exists.
    """
    pip_path = os.path.join(env_name, "bin", "pip") if os.name != "nt" else os.path.join(env_name, "Scripts", "pip")
    
    if os.path.exists(requirements_file):
        print(f"Installing dependencies from {requirements_file}...")
        subprocess.check_call([pip_path, "install", "-r", requirements_file])
        print("Dependencies installed successfully.")
    else:
        print(f"No {requirements_file} found. Skipping dependency installation.")

def main():
    """
    Main function to create, activate, and install dependencies in a virtual environment.
    """
    env_name = input("Enter the name of the virtual environment (default: env): ") or "env"
    requirements_file = input("Enter the path to requirements.txt (default: requirements.txt): ") or "requirements.txt"
    
    create_virtual_env(env_name)
    activate_virtual_env(env_name)
    install_dependencies(env_name, requirements_file)
    print("\nSetup complete!")

if __name__ == "__main__":
    main()
