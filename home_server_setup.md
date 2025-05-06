# Set Up NGINX Reverse Proxy on Raspberry

Here’s how you can expose your remote Raspberry Pi (on a 4G CG-NAT) to the internet via a second Raspberry Pi in your home with a public static IP using ZeroTier and reverse proxy

## 🔧 Step-by-Step Setup
### 1. Connect both Raspberry Pi devices to ZeroTier
On both Raspberry Pis (home & remote):
```bash
curl -s https://install.zerotier.com | sudo bash
sudo zerotier-cli join 1d7193940401eecd # Your ZeroTier network ID
```
Then go to the ZeroTier Central and authorize both clients in your network.
### 2. Create a free subdomain in FreeDNS
Use a free DNS service like: https://freedns.afraid.org/subdomain/

Create an **A record pointing** to your home static IP address.

Example:
```
chaletserreta.crabdance.com → <Your Home Public Static IP>
```

### 3. Set Up a Reverse Proxy on the Home Pi
Install Nginx on the home Pi:
```bash
sudo apt update
sudo apt install nginx -y
```

### 4. Create an NGINX config for your subdomain
Run:
```bash
sudo nano /etc/nginx/sites-available/chaletserreta
```
Paste this (replace ZEROTIER_REMOTE_IP with the ZeroTier IP of the remote Raspberry Pi):
```nginx
server {
    listen 80;
    server_name chaletserreta.crabdance.com;

    location / {
        proxy_pass http://10.144.169.135:5000;  # Replace with your Flask port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Enable this site:
```bash
sudo ln -s /etc/nginx/sites-available/chaletserreta /etc/nginx/sites-enabled/
sudo nginx -t  # Check for syntax errors
sudo systemctl reload nginx # Restart the automatic service
```

### 6. Home Router Port Forwarding
Make sure port 80 (HTTP) and 443 (HTTPS) are forwarded on your home router to your home Raspberry Pi’s local IP.

Once all of this is set:

* When a user opens http://chaletserreta.crabdance.com, it will go to your home Raspberry Pi.

* The home Raspberry Pi will forward the request over ZeroTier to your remote Raspberry Pi, which serves the web content.

## 7. ✅ Steps to Enable HTTPS on ```chaletserreta.crabdance.com```
### 7.1 Install Certbot and NGINX plugin
Run this on your home Raspberry Pi (the one with the public IP and NGINX):
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### 7.2 Make sure your DNS is ready
Check:
* ```chaletserreta.crabdance.com``` points to your home public IP.
* Port 80 (HTTP) is open and forwarded to your home Raspberry Pi.
* Port 443 (HTTPS) should also be forwarded if you want HTTPS to work.
Use this to test:
```bash
curl http://chaletserreta.crabdance.com
```
If you see a response (like the default NGINX page or your app), you're good to go.

### 7.3 Obtain and auto-configure SSL certificate
Run this command. You will have to introduce your email:
```bash
sudo certbot --nginx -d chaletserreta.crabdance.com
```
Certbot will:

* Get the SSL certificate

* Edit your NGINX config

* Enable HTTPS

* Set up automatic renewal

Follow the prompts — choose to redirect HTTP to HTTPS when asked.
### 7.4 Test HTTPS
Open in your browser: https://chaletserreta.crabdance.com

You should see your site with a secure lock 🔒 in the browser.

### 7.5 Renewal (automatic)
Certbot installs a cron job to auto-renew the cert. You can manually test it with:
```bash
sudo certbot renew --dry-run
```
