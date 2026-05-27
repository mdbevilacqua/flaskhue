#!/usr/bin/python3

from flask import Flask, redirect, render_template_string
import requests
import configparser
from typing import List, Dict

app = Flask(__name__)

# ========================= CONFIG =========================
config = configparser.ConfigParser()
config.read("hueconf")

HUE_IP = config["mylaptop"]["hue_host"]
HUE_KEY = config["mylaptop"]["hue_key"]
HUE_BASE = f"http://{HUE_IP}/api/{HUE_KEY}"
HOSTNAME = "192.168.0.101"


# ====================== LIGHT GROUPS ======================
GROUPS: Dict[str, Dict] = {
    "liv": {
        "name": "Living",
        "lights": ["2", "4", "5", "15", "23", "27", "28", "29", "30"],
        "routes": ["on", "med", "low", "off"]
    },
    "desk": {
        "name": "Office",
        "lights": ["12", "17", "18", "22"],
        "routes": ["on", "med", "off"]
    },
    "bed": {
        "name": "Bed",
        "lights": ["1", "7"],
        "routes": ["on", "med", "low", "off"]
    },
    "din": {
        "name": "Kitchen",
        "lights": ["3", "6", "10", "11"],
        "routes": ["on", "med", "off"]
    },
    "por": {
        "name": "Porch",
        "lights": ["8", "16", "19", "9", "20", "21"],
        "routes": ["on", "off"]
    }
}

# ====================== PAYLOADS ======================
PAYLOADS = {
    "on":  {"on": True,  "bri": 255},
    "med": {"on": True,  "bri": 177},
    "low": {"on": True,  "bri": 65},
    "off": {"on": False},
}

# Special cases for Living Room "med" and "low"
LIV_SPECIAL = {
    "med": {
        "23": {"on": True, "bri": 50},
        "29": {"on": True, "bri": 50},
        "30": {"on": True, "bri": 50},
        "5":  {"on": True, "bri": 100},
    },
    "low": {
        "23": {"on": True, "bri": 20},
        "29": {"on": True, "bri": 20},
        "30": {"on": True, "bri": 20},
    }
}

session = requests.Session()

# ====================== HELPERS ======================
def put_lights(lights: List[str], payload: dict):
    for light in lights:
        url = f"{HUE_BASE}/lights/{light}/state"
        try:
            session.put(url, json=payload, timeout=5)
        except requests.RequestException:
            pass  # Fail silently or log

def get_all_lights() -> Dict:
    """Return dict of light_id -> (name, is_on)"""
    try:
        r = session.get(f"{HUE_BASE}/lights", timeout=8)
        data = r.json()
        
        lights = {}
        for lid, info in data.items():
            lights[int(lid)] = (info["name"], info["state"].get("on", False))
        return lights
    except Exception:
        return {}

# ====================== HTML TEMPLATE ======================
HTML_TEMPLATE = """
<!DOCTYPE HTML>
<html>
<head><title>{{ hostname }}</title></head>
<body bgcolor="#000000">
<center>
<font color="white" size="5">
<big><big><big>
<b>{{ hostname }}</b><br><br>

{% for group in groups %}
    <a style="color:green">{{ group.name }}</a>&nbsp;&nbsp;&nbsp;&nbsp;
    {% for action in group.routes %}
        <a style="color:white" href="/lights-{{ group.key }}-{{ action }}/">{{ action|capitalize }}</a>&nbsp;&nbsp;&nbsp;&nbsp;
    {% endfor %}
    <br>

    {% for light_id, (name, is_on) in lights.items() if light_id in group.light_ids %}
        <a style="color:{{ 'magenta' if is_on else 'blue' }}" 
           href="/lights-{{ group.key }}-med/">{{ name }}</a><br>
    {% endfor %}
    <br>
{% endfor %}

</big></big></big>
</font>
</center>
</body>
</html>
"""

# ====================== ROUTES ======================
@app.route("/")
def index():
    lights = get_all_lights()
    
    # Prepare groups with light IDs for easy filtering
    group_data = []
    for key, g in GROUPS.items():
        group_data.append({
            "key": key,
            "name": g["name"],
            "routes": g["routes"],
            "light_ids": {int(lid) for lid in g["lights"]}
        })
    
    return render_template_string(HTML_TEMPLATE, 
                                hostname=HOSTNAME, 
                                groups=group_data, 
                                lights=lights)

def create_group_route(group_key: str, action: str):
    """Factory to create route handlers"""
    def handler():
        group = GROUPS[group_key]
        lights = group["lights"]
        
        if action == "med" and group_key == "liv":
            # Special handling for Living Room
            for light, payload in LIV_SPECIAL["med"].items():
                put_lights([light], payload)
            # Default for rest
            default_lights = [l for l in lights if l not in LIV_SPECIAL["med"]]
            put_lights(default_lights, {**PAYLOADS["med"], "ct": 500})
        elif action == "low" and group_key == "liv":
            for light, payload in LIV_SPECIAL["low"].items():
                put_lights([light], payload)
            default_lights = [l for l in lights if l not in LIV_SPECIAL["low"]]
            put_lights(default_lights, {**PAYLOADS["low"], "ct": 500})
        else:
            payload = PAYLOADS[action].copy()
            if action != "off":
                payload["ct"] = 500 if group_key == "liv" else 255
            put_lights(lights, payload)
        
        return redirect(f"http://{HOSTNAME}", code=302)
    
    handler.__name__ = f"set_lights_{group_key}_{action}"
    return handler

# Dynamically create all routes
for group_key, group in GROUPS.items():
    for action in group["routes"]:
        route = f"/lights-{group_key}-{action}/"
        app.add_url_rule(route, view_func=create_group_route(group_key, action))

if __name__ == "__main__":
    app.run(debug=True)
