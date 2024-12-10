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
