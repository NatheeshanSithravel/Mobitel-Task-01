import sys
import paramiko
import maskpass

def run_remote_command(client, command):
    """Execute a command on the remote server."""
    try:
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode().strip())
        error = stderr.read().decode().strip()
        if error:
            print(f"Error: {error}")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to execute command: {e}")
        sys.exit(1)

def ssh_to_server(hostname, username, password=None):
    """Establish an SSH connection to the server."""
    print(f"Connecting to {hostname} as {username}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=hostname, username=username, password=password)
        print("Connected successfully.")
        return client
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your username/password.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to connect to {hostname}: {e}")
        sys.exit(1)

def deploy_frontend(client, img_tag):
    """Deploy the frontend container image."""
    print(f"Deploying frontend image: {img_tag}")
    run_remote_command(client, f"docker pull registry-gitlab.arimaclanka.com/arimac-mobitel/web-frontend:{img_tag}")
    run_remote_command(client, f"docker tag registry-gitlab.arimaclanka.com/arimac-mobitel/web-frontend:{img_tag} pr-docker-reg.mobitel.lk/sltmobitel/web-frontend:{img_tag}")
    run_remote_command(client, f"docker push pr-docker-reg.mobitel.lk/sltmobitel/web-frontend:{img_tag}")

def deploy_backend(client, img_tag):
    """Deploy the backend container image."""
    print(f"Deploying backend image: {img_tag}")
    run_remote_command(client, f"docker pull registry-gitlab.arimaclanka.com/arimac-mobitel/web-backend:{img_tag}")
    run_remote_command(client, f"docker tag registry-gitlab.arimaclanka.com/arimac-mobitel/web-backend:{img_tag} pr-docker-reg.mobitel.lk/sltmobitel/app-backend:{img_tag}")
    run_remote_command(client, f"docker push pr-docker-reg.mobitel.lk/sltmobitel/app-backend:{img_tag}")

def deploy_images(client):
    """Handle deployment logic for frontend and backend images."""
    backend_img = input("Enter Backend image tag (leave blank if not deploying backend): ").strip()
    frontend_img = input("Enter Frontend image tag (leave blank if not deploying frontend): ").strip()

    if not backend_img and not frontend_img:
        print("Error: No image tags provided. Exiting.")
        sys.exit(1)

    if backend_img:
        deploy_backend(client, backend_img)
    if frontend_img:
        deploy_frontend(client, frontend_img)

def main():
    """Main entry point for the script."""
    hostname = "192.168.56.101"
    username = input("Enter your username for SSH connection: ").strip()
    password = maskpass.advpass() 
    

    client = ssh_to_server(hostname, username, password)
    try:
        deploy_images(client)
    finally:
        print("Closing SSH connection.")
        client.close()

if __name__ == "__main__":
    main()
