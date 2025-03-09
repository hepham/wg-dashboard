# WGDashboard

WGDashboard is a web application built with Flask that allows for the management and configuration of peers in WireGuard. This application provides a user interface to create, edit, and delete peers, as well as monitor their status and related information.

## Features

- Create and manage WireGuard peers.
- Display detailed information about peers, including IP addresses, public keys, and connection status.
- Generate QR codes for peers to easily share configurations.
- Automatically refresh information about peers and connection statuses.
- Support for DNS configuration and other options for each peer.

## Requirements

- Python 3.8 or higher
- Flask
- TinyDB
- Flask-Qrcode
- Other libraries listed in `requirements.txt`

## Installation

1. Clone this repository to your machine:

   ```bash
   git clone https://github.com/yourusername/WGDashboard.git
   cd WGDashboard
   ```

2. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the configuration file for the application. You can create a sample configuration file based on `config.ini.example`.

4. Run the application:

   ```bash
   python app.py
   ```
```
WGDashboard/
│
├── app.py # Main file of the Flask application
├── models/ # Contains data models
│ ├── dashboard_model.py
│ └── wireguard_model.py
├── views/ # Contains views of the application
│ ├── auth_views.py
│ ├── config_views.py
│ ├── dashboard_views.py
│ ├── settings_views.py
│ └── peer_views.py
├── templates/ # Contains HTML files for the user interface
│ └── get_conf.html
├── static/ # Contains static files (CSS, JS, images)
├── config.py # Configuration file for the application
└── requirements.txt # List of required libraries
```
5. Access the application through your browser at `http://localhost:10086`.

## Directory Structure

## Contribution

If you would like to contribute or report issues, please open an issue on GitHub or submit a pull request.

## License

This project is licensed under the MIT License. Please see the LICENSE file for more details.
