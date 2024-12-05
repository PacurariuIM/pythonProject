# Setting Up a Gunicorn Server on Hetzner Cloud for a Flask App

This guide walks you through deploying a Flask app on a Hetzner Cloud server using Gunicorn. It covers setting up the server, cloning the app, and configuring Gunicorn to serve the app.

## 1. Set Up a Hetzner Cloud Server

### Step 1: Create a Hetzner Cloud Account and Project

Log in to Hetzner Cloud Console.
Create a new Project for your app.

### Step 2: Create a Server
#### 1. Inside your project, click Create Server and configure:
        Location: Choose a European data center (e.g., Germany or Finland).
        Image: Select Ubuntu 22.04 LTS (recommended for stability).
        Server Type: Use a small instance, such as CX11, for simple apps.
        SSH Key: Add your public SSH key for secure access.
#### 2. Note the IP address of your server

### Step 3: Access Your Server

```sh
ssh root@<server-ip>
```

## 2. Prepare Your Server
### Step 1: Update the System
```sh
apt update && apt upgrade -y
```
### Step 2: Install Required Packages
```sh
apt install python3 python3-venv python3-pip git -y
```
### Step 3: Create a Non-Root User
For security, create a new user for managing your app:
```sh
adduser myuser
usermod -aG sudo myuser
```
Switch to the new user:
```sh
su - myuser
```

### Step 4: Clone Your Flask App
Clone your app's repo to the server and navigate into the app directory:
```sh
git clone https://github.com/<your-username>/<your-repo>.git

cd <your-repo>
```

### Step 5: Set Up a Python Virtual Environment

Create and activate a virtual environment:
```sh
python3 -m venv venv
source venv/bin/activate
```
Install your app’s dependencies:
```sh
pip install -r requirements.txt
```

## 3. Test Your Flask App Locally
```sh
python main.py
```
## 4. Configure Gunicorn
### Step 1: Install Gunicorn
Inside your virtual environment, install Gunicorn:
```sh
pip install gunicorn
```
### Step 2: Run Gunicorn Manually
Test your app with Gunicorn:
```sh
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```
- w 4: Number of worker processes.
- b 0.0.0.0:8000: Bind to all interfaces on port 8000.
- Replace main:app with the module and app name in your project.
- Visit `http://your-server-ip:8000` in a browser to confirm the app is running.

## 5. Set Up Gunicorn as a Systemd Service
### Step 1: Create a Systemd Service File
Create a new service file:
```sh
sudo nano /etc/systemd/system/<your-app-name>.service
```
Add the following configuration:
```ini
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=myuser
Group=www-data
WorkingDirectory=/home/myuser/<your-repo>
Environment="PATH=/home/myuser/<your-repo>/venv/bin"
ExecStart=/home/myuser/<your-repo>/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 main:app

[Install]
WantedBy=multi-user.target
```
(replace myuser, your-repo with your own)

### Step 2: Start and Enable the Service
Reload the systemd daemon:
```sh
sudo systemctl daemon-reload
```
Start the service:
```sh
sudo systemctl start <your-app-name>
```
Enable the service to start on boot:
```sh
sudo systemctl enable <your-app-name>
```
Check the service status:
```sh
sudo systemctl status <your-app-name>
```

## 6. Configure Nginx (Optional)
To expose your app on standard HTTP ports (80/443) with domain support:

### Step 1: Install nginx
```sh
sudo apt install nginx -y
```
### Step 2: Configure Nginx to reverse proxy to Gunicorn
```sh
sudo nano /etc/nginx/sites-available/<your-app-name>
```
Add:
```nginx
server {
    listen 80;
    server_name <your-domain-or-server-ip>;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
### Step 3: Enable the configuration
```sh
sudo ln -s /etc/nginx/sites-available/<your-app-name> /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
## 7. Secure Your App with HTTPS
### Step 1: Install Certbot for Nginx
```sh
sudo apt install certbot python3-certbot-nginx -y
```
### Step 2: Obtain an SSL certificate
```sh
sudo certbot --nginx -d yourdomain.com
```
### Step 3: Test auto renewal
```sh
sudo certbot renew --dry-run
```

Install `fail2ban` to automatically block IPs that exhibit suspicious behavior. (optional)
```sh
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```