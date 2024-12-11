# CI/CD automation with Github Actions

##  Step 1: Set Up SSH Keys for GitHub Actions
**Objective**: Configure SSH key-based authentication to securely connect GitHub Actions to your Hetzner server.

### 1. Generate SSH Keys on Your Local Machine
Same as [here](ssh_gen.md), name it differently.
<p>Save the keys in a secure location</p>

### 2. Add the Public Key to Your Hetzner Server:
- Copy the public key:
```sh
cat ~/.ssh/github-actions-key.pub
```
- SSH into your server using your current credentials:
```sh
ssh root@your_server_ip
```
- Add the key to the authorized keys file:
```sh
echo "<PASTE_PUBLIC_KEY>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```
- Exit the server (`exit` in terminal), test the connection locally with the private key (replace `github-actions-key` and `YOUR_SERVER_IP` ):
```sh
ssh -i ~/.ssh/github-actions-key root@<YOUR_SERVER_IP>
```
### 3. Disable Password Authentication (Optional):
To secure your server, consider disabling password authentication for SSH.
- Edit the SSH configuration file:
```sh
sudo nano /etc/ssh/sshd_config
```
- Find and set these parameters (Ctrl+w):
```sh
PasswordAuthentication no
PermitRootLogin prohibit-password
```
- Restart the SSH service:
```sh
# Run to see all `ssh` files
systemctl list-units --type=service | grep ssh

# Depending on configuration
sudo systemctl restart ssh.service
#or
sudo systemctl restart ssh@.service
#or
sudo systemctl restart sshd
```
- Ensure the config is working:
```sh
sudo sshd -t
```

## Step 2: Add Secrets for Deployment
To automate deployment, we need to provide GitHub Actions with secure access to the server and deployment configuration. Here’s what to add as secrets:

### 1. SSH_PRIVATE_KEY:
- Go to your repository on GitHub.
- Navigate to Settings > Secrets and variables > Actions > New repository secret.
- Add the private key as a secret named SSH_PRIVATE_KEY.
### 2. SERVER_USER:
- This is the username you use to SSH into the server (e.g., root or non-root-user prefferably).
- Set Permissions for the Non-Root User
```sh
#File Permissions:
sudo chown -R user:user /var/www/myapp #replace with folder loc
```
- If the pipeline requires restarting services (like Nginx or your Flask app), you need to allow the deploy user to run sudo commands (such as systemctl to restart services) without a password:
```sh
#Sudo Privileges for Service Management:
sudo visudo
```
and add this line to sudoers file:
```sh
#add privileges as needed
my_user ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx, /bin/systemctl restart my-flask-app 
```

## Step 3: Create the GitHub Actions Workflow
The workflow file will be located in the `.github/workflows` directory. (create one, if it doesn't exist)

**Trigger**: The pipeline should trigger on pushes to the `main`branch.</p>
**Jobs:**: 
- Use the SSH key stored in GitHub Secrets.
- Deploy the code: Pull the latest code from the GitHub repository to the server and restart services.
- Rollback in case of failure: Add an option to roll back if something goes wrong.

### 1. Create the GitHub Actions Workflow File
- Create the directory structure if it doesn't already exist:
- Create a file named `deploy.yml` inside the `workflows` directory
- Open the file in VS Code
### 2. Define the Workflow YAML Configuration
Sammple code for `deploy.yml` (replace `/var/www/html` with path to project)
```yml
name: Deploy to Hetzner Server

# Trigger deployment on push to the main branch
on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code from GitHub
      uses: actions/checkout@v3

    - name: Set up SSH key
      uses: webfactory/ssh-agent@v0.5.3
      with:
        ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

    - name: Deploy to Hetzner server
      run: |
        ssh -o StrictHostKeyChecking=no ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_IP }} << 'EOF'
          cd /var/www/myapp || exit 1
          git pull origin main || exit 1
          # Optional: Run build or other tasks (e.g., pip install, npm install)
          sudo systemctl restart nginx || exit 1
          sudo systemctl restart my-flask-app || exit 1
        EOF
      env:
        SERVER_USER: ${{ secrets.SERVER_USER }}
        SERVER_IP: ${{ secrets.SERVER_IP }}

    - name: Check deployment status
      run: echo "Deployment successful!"
```

### 3. Commit and Push the Workflow File
### 4. Verify the Setup
Check GitHub Actions:
- Go to the Actions tab of your GitHub repository and verify that the workflow is running.
- Look for any issues in the logs, particularly around the SSH connection or deployment steps

Verify Deployment:
After the pipeline runs, verify that the code was successfully deployed to the server:
- Check that the server has the latest code from GitHub.
- Ensure that Nginx and your Flask app have been restarted correctly.