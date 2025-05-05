# PROYECTO NEVERA
Project to monitor the electricity supply in a remote house in the countryside. The continuity of the electricity supply is especially critical for the fridge and the food inside.

## How to set up the program?

Run the following commands in the Raspberry Pi:
```bash
#!/bin/bash

# Create the project directory
mkdir -p ~/ProyectoNevera
cd ~/ProyectoNevera

# Create the virtual environment
python3 -m venv ProyectoNevera

# Activate the virtual environment
source ProyectoNevera/bin/activate

# Upgrade pip (optional but recommended)
pip install --upgrade pip

# Install required Python packages
pip install adafruit-circuitpython-bme280 flask

echo "✅ Entorno virtual 'ProyectoNevera' creado y configurado con Flask y Adafruit BME280."
echo "💡 Para activarlo más adelante, ejecuta:"
echo "source ~/ProyectoNevera/ProyectoNevera/bin/activate"
```

- It is necessary to **create a virtual environment** to avoid library conflicts
- It is necessary to **activate the 2-steps verification** in the Google account
- It is necessary to create an **application password** in the Google account

## Automatic Start in the Raspberry Pi
### 1. Create a Bash Script
1. Create the script:
```bash
nano /home/pi/start_nevera_alert.sh
```
2. Add your commands:
```bash
#!/bin/bash
cd /home/pi/bme280_project/
source venv/bin/activate
python3 nevera_alert5.py
```
3. Save and exit with Ctrl+X, then Y, and Enter.

4. Make the script executable:
```bash
chmod +x /home/pi/start_nevera_alert.sh
```
### 2. Create a Systemd Service
1. Create the service file:
```bash
sudo nano /etc/systemd/system/nevera_alert.service
```
2. Add the following content:
```ini
[Unit]
Description=Nevera Alert Script
After=network.target

[Service]
ExecStart=/bin/bash /home/pi/bme280_project/start_nevera_alert.sh
Restart=always
User=pi
WorkingDirectory=/home/pi/bme280_project/

[Install]
WantedBy=multi-user.target
```
3. Save and exit.

### 3. Enable and Start the Service

1. Reload the systemd manager to recognize the new service:
```bash
sudo systemctl daemon-reload
```
2. Enable the service to run at boot:
```bash
sudo systemctl enable nevera_alert.service
```
3. Start the service immediately:
```bash
sudo systemctl start nevera_alert.service
```
4. Check the status to confirm it’s running:
```bash
sudo systemctl status nevera_alert.service
```
5. Stop the programmed process if you need:
```bash
sudo systemctl stop nevera_alert.service
```

### 4. Monitor Logs (Optional)
If something goes wrong, you can check logs with:
```bash
journalctl -u nevera_alert.service -f
```