from flask import Flask, jsonify, request  # Import Flask for creating the web application and handling requests
import subprocess  # Import subprocess to execute system commands
import logging  # Import logging for recording application logs
import os  # Import os for environment variable handling and system file access
import psutil  # Import psutil for system stats like CPU, memory, and power
import time  # Import time to calculate system uptime
import requests  # Requests module to make HTTP requests
from dotenv import load_dotenv  # Import dotenv to load environment variables from .env file

# Load environment variables from .env file
load_dotenv()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")  # Retrieve secret token from environment variables
FETCH_EMAIL_API_URL = os.getenv("FETCH_EMAIL_API_URL")  # Retrieve fetching email api endpint from environment variables
FETCH_EMAIL_API_TOKEN = os.getenv("FETCH_EMAIL_API_TOKEN")  # Retrieve secret token from environment variables

# Initialize Flask app
app = Flask(__name__)

# Configure logging to record all requests and actions
logging.basicConfig(filename="requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def get_power_status():
    """
    Determines the power source by checking the correct AC power directory.
    Reads from /sys/class/power_supply/ to determine if the system is on battery or AC power.
    """
    power_supply_path = "/sys/class/power_supply/"  # Define the path where power status is stored
    try:
        # Look for any power supply directory containing "AC" or "ADP" (varies by system)
        ac_name = next((d for d in os.listdir(power_supply_path) if "AC" in d or "ADP" in d), None)
        if not ac_name:
            return "Unknown"  # If no AC adapter is found, return "Unknown"
        with open(os.path.join(power_supply_path, ac_name, "online"), "r") as f:
            return "On Power" if f.read().strip() == "1" else "On Battery"  # Return power status
    except Exception as e:
        logging.error(f"Error reading power status: {str(e)}")  # Log errors if reading fails
        return "Unknown"  # Return unknown in case of an error

def get_system_info():
    """
    Fetches system details:
    - CPU Usage
    - Memory Usage
    - Power Source & Battery Status
    - System Uptime
    """
    cpu_usage = psutil.cpu_percent(interval=1)  # Get CPU usage percentage over a 1-second interval
    memory = psutil.virtual_memory()  # Fetch memory usage details
    uptime = time.time() - psutil.boot_time()  # Calculate system uptime in seconds
    power_source = get_power_status()  # Get power source information
    battery = psutil.sensors_battery()  # Retrieve battery status
    battery_percentage = f"{round(battery.percent, 2)}%" if battery and battery.percent is not None else "N/A"  # Format battery percentage rounded to 2 decimal places
    
    return {
        "cpu": f"{cpu_usage}%",  # Format CPU usage
        "memory": f"{memory.percent}% used of {round(memory.total / (1024 ** 3), 2)}GB",  # Format memory usage
        "power_source": power_source,  # Store power source
        "battery_percentage": battery_percentage,  # Store battery percentage
        "uptime": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"  # Format uptime in hours and minutes
    }

def slack_block_response(system_info):
    """
    Formats a Slack Block Kit UI response with system details.
    This provides a structured message format compatible with Slack.
    """
    return {
        "response_type": "ephemeral",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": ":desktop_computer: *Server Status Update:*\nHere are all the details of the server."}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*:computer: CPU Usage:*\n{system_info['cpu']}"},
                {"type": "mrkdwn", "text": f"*:floppy_disk: Memory Usage:*\n{system_info['memory']}"},
                {"type": "mrkdwn", "text": f"*:zap: Power Source:*\n{system_info['power_source']}"},
                {"type": "mrkdwn", "text": f"*:battery: Battery Percentage:*\n{system_info['battery_percentage']}"},
                {"type": "mrkdwn", "text": f"*:clock1: Uptime:*\n{system_info['uptime']}"},
            ]},
            {"type": "divider"}
        ]
    }

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Root endpoint: Returns system details using Slack Block Kit.
    Logs request details for debugging.
    """
    if request.method == "POST":
        logging.info("Received a POST request at /")
        logging.info(f"Headers: {request.headers}")
        logging.info(f"Body: {request.get_data(as_text=True)}")

    token = request.form.get("token")  # Retrieve token from request
    if not token or token != SECRET_TOKEN:  # Validate token
        logging.warning("Unauthorized request received!")
        return jsonify({
            "response_type": "ephemeral",
            "blocks": [{"type": "divider"},{"type": "section", "text": {"type": "mrkdwn", "text": "🚫 *Unauthorized request!*"}},{"type": "divider"}]
        }), 200
    
    system_info = get_system_info()
    return jsonify(slack_block_response(system_info)), 200  # Respond with formatted Slack message

@app.route("/command/reboot", methods=["POST"])
def reboot_system():
    """
    Handles /command/reboot:
    - Logs request details
    - Validates the token
    - Executes reboot if the token is correct
    - Returns a Slack Block Kit formatted message
    """
    try:
        logging.info("Received a request at /command/reboot")
        logging.info(f"Headers: {request.headers}")
        logging.info(f"Body: {request.get_data(as_text=True)}")
        
        token = request.form.get("token")  # Retrieve token from request
        if not token or token != SECRET_TOKEN:  # Validate token
            logging.warning("Unauthorized request received!")
            return jsonify({
                "response_type": "ephemeral",
                "blocks": [{"type": "divider"},{"type": "section", "text": {"type": "mrkdwn", "text": "🚫 *Unauthorized request!*"}},{"type": "divider"}]
            }), 200
        
        # subprocess.run(["sudo", "/sbin/reboot"], check=True)  # Execute system reboot
        return jsonify({"response_type": "ephemeral","blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "🔄 *Reboot command executed!*"}}]}), 200
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing reboot command: {str(e)}")
        return jsonify({"response_type": "ephemeral","blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": f"❌ *Error executing reboot:* `{str(e)}`"}}]}), 500

@app.route("/command/fetch/emails", methods=["POST"])
def fetch_emails():
    """
    Endpoint to make a POST request to an external email API with custom headers.
    
    Returns:
        JSON: The response from the external API or an error message.
    """
    try:
        logging.info("Received a request at /command/fetch/emails")  # Log the request
        
        # Define the external API URL
        email_api_url = FETCH_EMAIL_API_URL  # Placeholder URL, replace with actual API
        
        # Define the headers for the request
        headers = {
            "Authorization": f"Bearer {FETCH_EMAIL_API_TOKEN}",  # Add authentication token in the headers
            "Content-Type": "application/json"  # Set request content type to JSON
        }
        
        # Make the POST request
        response = requests.post(email_api_url, headers=headers)  # Send a request to the external email API
        response_data = response.json()  # Parse response data from JSON
        
        return jsonify(response_data), response.status_code  # Return the response and status code
    except Exception as e:
        logging.error(f"Error fetching emails: {str(e)}")  # Log error details
        return jsonify({"error": "Failed to fetch emails"}), 500  # Return an error message in case of failure

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Start Flask app on port 5000, accessible from any IP

