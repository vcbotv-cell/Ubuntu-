import os
import random
import string
import subprocess
import threading
import requests

from flask import Flask, render_template_string

app = Flask(__name__)

# ==============================
# CLOUDFLARE CONFIG
# ==============================

CF_API_TOKEN = os.getenv("C_TOKEN")

CF_ZONE_ID = "83c49b52d6ffe95c9615f424ece7c2e9"

DOMAIN = "co08.art"

# ==============================
# RANDOM SUBDOMAIN
# ==============================

def random_subdomain():
    # Example:
    # ip-17-29-05-yy-6yy

    a = random.randint(10, 99)
    b = random.randint(10, 99)
    c = random.randint(10, 99)

    letters = ''.join(
        random.choices(string.ascii_lowercase, k=2)
    )

    number = random.randint(100, 999)

    return f"ip-{a}-{b}-{c}-{letters}-{number}"


# ==============================
# RAILWAY URL
# ==============================

def get_railway_url():

    # Railway normally provides RAILWAY_PUBLIC_DOMAIN
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")

    if railway_domain:
        return f"https://{railway_domain}"

    # Fallback
    railway_static = os.getenv("RAILWAY_STATIC_URL")

    if railway_static:
        if railway_static.startswith("http"):
            return railway_static

        return f"https://{railway_static}"

    # Manual fallback
    return "http://localhost:8080"


# ==============================
# CLOUDFLARE DNS
# ==============================

def create_cloudflare_record(subdomain, target):

    if not CF_API_TOKEN:
        print("ERROR: C_TOKEN is not set.")
        return False

    url = (
        f"https://api.cloudflare.com/client/v4/"
        f"zones/{CF_ZONE_ID}/dns_records"
    )

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    full_domain = f"{subdomain}.{DOMAIN}"

    data = {
        "type": "CNAME",
        "name": full_domain,
        "content": target.replace("https://", "").replace("http://", "").rstrip("/"),
        "ttl": 1,
        "proxied": False
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        result = response.json()

        if result.get("success"):
            print(f"[+] DNS CREATED: {full_domain}")
            print(f"[+] TARGET: {target}")

            return True

        print("[!] Cloudflare error:")
        print(result)

        return False

    except Exception as e:

        print("[!] Cloudflare request failed:")
        print(e)

        return False


# ==============================
# CREATE DOMAIN
# ==============================

def setup_domain():

    railway_url = get_railway_url()

    print("=" * 50)
    print("R-BOTS DOMAIN SYSTEM")
    print("=" * 50)

    print(f"Railway URL: {railway_url}")

    if not CF_API_TOKEN:
        print("C_TOKEN is missing.")
        return "C_TOKEN not configured"

    for _ in range(10):

        subdomain = random_subdomain()

        if create_cloudflare_record(
            subdomain,
            railway_url
        ):

            return f"https://{subdomain}.{DOMAIN}"

    return "Failed to create Cloudflare domain"


# ==============================
# HTML
# ==============================

HTML = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>R-BOTS SSH</title>

<style>

body {
    margin: 0;
    background: #0b0b0b;
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.card {
    width: 90%;
    max-width: 550px;
    background: #151515;
    padding: 30px;
    border-radius: 18px;
    box-shadow: 0 0 30px #000;
    text-align: center;
}

h1 {
    margin-bottom: 25px;
}

.domain {
    background: #080808;
    padding: 15px;
    border-radius: 10px;
    word-break: break-all;
    margin-bottom: 15px;
    font-size: 16px;
}

button {
    width: 100%;
    padding: 13px;
    border: 0;
    border-radius: 10px;
    cursor: pointer;
    font-size: 16px;
    font-weight: bold;
}

.copy {
    background: white;
    color: black;
}

.copy:hover {
    opacity: .85;
}

.status {
    margin-top: 20px;
    color: #aaa;
    font-size: 14px;
}

</style>

</head>

<body>

<div class="card">

<h1>R-BOTS SSH ACCESS</h1>

<div class="domain" id="domain">
{{ domain }}
</div>

<button class="copy"
onclick="copyDomain()">

COPY DOMAIN

</button>

<div class="status" id="status">
Cloudflare DNS Connected
</div>

</div>

<script>

function copyDomain() {

    const domain =
        document.getElementById("domain").innerText;

    navigator.clipboard.writeText(domain);

    document.getElementById("status").innerText =
        "✓ Domain copied";

}

</script>

</body>

</html>
"""


# ==============================
# ROUTE
# ==============================

@app.route("/")
def home():

    domain = setup_domain()

    return render_template_string(
        HTML,
        domain=domain
    )


# ==============================
# START TTYD
# ==============================

def start_ttyd():

    port = os.getenv("PORT", "8080")

    username = os.getenv("USERNAME", "root")
    password = os.getenv("PASSWORD", "root")

    command = [
        "/bin/ttyd",
        "-p",
        port,
        "-W",
        "-c",
        f"{username}:{password}",
        "/bin/bash"
    ]

    print(f"[+] Starting ttyd on port {port}")

    subprocess.Popen(command)


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    threading.Thread(
        target=start_ttyd,
        daemon=True
    ).start()

    port = int(os.getenv("PORT", "8080"))

    print(f"[+] Web server starting on {port}")

    app.run(
        host="0.0.0.0",
        port=port
    )
