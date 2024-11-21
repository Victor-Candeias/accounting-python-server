import subprocess
import sys

def run_command(command):
    """Helper function to run a shell command and print the output."""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e.stderr}")
        sys.exit(1)

def install_mongo_docker():
    """Install MongoDB Docker image and run the container."""
    # Ask for container name
    container_name = input("Enter a name for your MongoDB container: ").strip() or "mongo_container"
    
    # Pull MongoDB image from Docker Hub
    print("Pulling MongoDB Docker image...")
    run_command(["docker", "pull", "mongo"])

    # Run MongoDB container
    print(f"Running MongoDB container with name '{container_name}'...")
    run_command(["docker", "run", "--name", container_name, "-d", "-p", "27017:27017", "mongo"])

    # Check if the container is running
    print("Verifying MongoDB container is running...")
    run_command(["docker", "ps"])

    # Print the MongoDB connection string
    connection_string = f"mongodb://localhost:27017"
    print(f"\nMongoDB is running. You can connect to it using the following connection string:\n{connection_string}")

def stop_and_remove_container(container_name):
    """Stop and remove MongoDB container."""
    print(f"Stopping and removing the container '{container_name}'...")
    run_command(["docker", "stop", container_name])
    run_command(["docker", "rm", container_name])

if __name__ == "__main__":
    install_mongo_docker()

    # Optionally stop and remove the container after installation
    # Uncomment the line below if you want to stop and remove the container
    # stop_and_remove_container(container_name)
