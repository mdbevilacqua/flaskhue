# Simple Flask WebUI Example for Controlling Philips Hue Lights

## Setup:

Install jq(1). Setup your hue bridge API key using the key_gen.sh script. 

bash key_gen.sh

Copy the key into 'hueconf'


## Setup the python3 environment:
python -m venv venv
pip install -r requirements.txt
source venv/bin/activate


Run and debug with:
venv/bin/gunicorn --workers 4 --max-requests-jitter 100 --access-logfile logs/access.log --error-logfile logs/error.log --bind "192.168.0.100:8099" flaskhue:app


## Simple example service file for systemd as root:

[Unit]\
Description=flaskhue gunicorn daemon\
After=network.target

[Service}\
User=root\
Group=root\
WorkingDirectory=/root/flaskhue\
Environment="PATH=/root/flaskhue/venv_flaskhue/bin"\
ExecStart=/root/flaskhue/venv_flaskhue/bin/gunicorn --workers 4 --max-requests-jitter 100 --access-logfile /root/flaskhue/logs/access.log --error-logfile /root/flaskhue/logs/error.log --bind "192.168.0.100:80" flaskhue:app

[Install]\
WantedBy=multi-user.target

