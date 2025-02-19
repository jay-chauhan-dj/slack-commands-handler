# 🚀 Flask Slack Slash Commands API

This Flask application serves as a backend for Slack Slash Commands. It supports various system-related commands, including fetching system status and executing administrative tasks.

## ✨ Features
- 💬 **Slack-compatible response formatting**
- 🖥️ **Fetch CPU, memory, and uptime details**
- 🔋 **Detect power source (AC/Battery) and battery percentage**
- 🔒 **Secure execution of system-level commands (e.g., reboot)**
- 🏗️ **Extendable architecture for additional Slack commands**
- 📜 **Logs all incoming requests for auditing**

## 🛠 Prerequisites
Before setting up the application, ensure you have:
- ![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python) Python 3.7 or later
Before setting up the application, ensure you have:
- 📦 `pip` installed
- 🖥️ A Linux-based system (recommended) to fetch battery and power details
- 🔑 A `.env` file with the `SECRET_TOKEN` for secure access
- 🔗 A configured Slack app with Slash Commands

## 📥 Installation
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-repository/slack-commands-handler.git
cd slack-commands-handler
```

### 2️⃣ Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create and Configure the `.env` File
```bash
echo "SECRET_TOKEN=your_secret_token" > .env
```
Replace `your_secret_token` with a secure key.

## 🚀 Running the Application
Start the Flask server with:
```bash
python app.py
```
By default, the app runs on `http://0.0.0.0:5000`.

## 🔌 API Endpoints
### `/` (GET, POST)
Returns system status details in a Slack-compatible format.

### `/command/reboot` (POST)
Reboots the system if the request contains the correct `SECRET_TOKEN`.
```bash
curl -X POST -d "token=your_secret_token" http://localhost:5000/command/reboot
```

### 🔮 Future Commands
- Additional Slack Slash Commands can be added to handle different system operations.
- Extend functionality to support disk space monitoring, network status, or service restarts.

## 🚀 Deploying with Gunicorn
For production, use **Gunicorn**:
```bash
pip install gunicorn
```
Run the application with:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🏠 Hosting as a Systemd Service
To ensure the Flask app runs as a background service, create a systemd service file.

### 1️⃣ Create the Service File
```bash
sudo nano /etc/systemd/system/slack-commands-handler.service
```

### 2️⃣ Add the Following Content
```ini
[Unit]
Description=Flask Slack Slash Commands API Service
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
Environment="SECRET_TOKEN=your_secret_token"

[Install]
WantedBy=multi-user.target
```
Replace `your_user` and `/path/to/your/app` accordingly.

### 3️⃣ Enable and Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable flask_slack_commands
sudo systemctl start flask_slack_commands
```

### 4️⃣ Check Service Status
```bash
sudo systemctl status flask_slack_commands
```

## 📜 Logging
All request logs are stored in `requests.log`.

## 🤝 Contributing
Feel free to submit issues and pull requests.

## 🏷 License
MIT License

## 👤 Owner Details
- **👨‍💻 Name:** Jay Chauhan
- **📧 Email:** [contact@dj-jay.in](mailto:contact@dj-jay.in)
- **🌐 Website:** [www.dj-jay.in](https://www.dj-jay.in)
- **📞 Contact Number:** +91 93134 40532
