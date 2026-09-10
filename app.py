import os
import subprocess
import threading
import requests

from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# VERCEL CLOUDFLARE API
# ==========================================

VERCEL_API = "https://co08-cloudflare-api.vercel.app/api/create-domain"


# ==========================================
# GET RAILWAY PUBLIC URL
# ==========================================

def get_railway_url():

    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")

    if domain:
        return "https://" + domain

    static_url = os.getenv("RAILWAY_STATIC_URL")

    if static_url:
        if static_url.startswith("http"):
            return static_url

        return "https://" + static_url

    return ""


# ==========================================
# CREATE CLOUDFLARE DOMAIN
# ==========================================

def create_domain():

    railway_url = get_railway_url()

    if not railway_url:
        return {
            "success": False,
            "error": "Railway public domain not detected"
        }

    try:

        response = requests.post(
            VERCEL_API,
            json={
                "target": railway_url
            },
            timeout=30
        )

        return response.json()

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ==========================================
# HTML
# ==========================================

HTML = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>R-BOTS SSH ACCESS</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #080808;
    color: #fff;

    font-family: Arial, sans-serif;
}

.card {

    width: 92%;
    max-width: 560px;

    background: #151515;

    border: 1px solid #292929;

    border-radius: 18px;

    padding: 30px;

    text-align: center;

    box-shadow: 0 20px 60px rgba(0,0,0,.5);
}

.title {

    font-size: 24px;
    font-weight: bold;

    margin-bottom: 25px;
}

.domain {

    background: #090909;

    border: 1px solid #292929;

    border-radius: 10px;

    padding: 15px;

    word-break: break-all;

    margin-bottom: 15px;

    font-size: 15px;
}

button {

    width: 100%;

    border: 0;

    border-radius: 10px;

    padding: 14px;

    background: #fff;

    color: #000;

    font-size: 15px;

    font-weight: bold;

    cursor: pointer;
}

button:active {

    transform: scale(.98);
}

.status {

    margin-top: 18px;

    color: #999;

    font-size: 14px;
}

.error {

    color: #ff5f5f;
}

.success {

    color: #5cff9d;
}

</style>

</head>

<body>

<div class="card">

<div class="title">
R-BOTS SSH ACCESS
</div>

<div class="domain" id="domain">
{{ domain }}
</div>

<button onclick="copyDomain()">
COPY DOMAIN
</button>

<div class="status {{ status_class }}" id="status">
{{ status }}
</div>

</div>


<script>

function copyDomain() {

    const domain =
        document.getElementById("domain").innerText.trim();

    navigator.clipboard.writeText(domain);

    document.getElementById("status").innerText =
        "✓ Domain copied";

    document.getElementById("status").className =
        "status success";
}

</script>

</body>

</html>
"""


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    result = create_domain()

    if result.get("success"):

        domain = result.get(
            "url",
            result.get("domain", "Domain created")
        )

        status = "✓ Cloudflare domain created"

        status_class = "success"

    else:

        domain = "Failed to create Cloudflare domain"

        status = result.get(
            "error",
            "Unknown error"
        )

        status_class = "error"

    return render_template_string(
        HTML,
        domain=domain,
        status=status,
        status_class=status_class
    )


# ==========================================
# TTYD
# ==========================================

def start_ttyd():

    port = os.getenv("PORT", "8080")

    username = os.getenv(
        "USERNAME",
        "root"
    )

    password = os.getenv(
        "PASSWORD",
        "root"
    )

    command = [
        "/bin/ttyd",
        "-p",
        port,
        "-W",
        "-c",
        f"{username}:{password}",
        "/bin/bash"
    ]

    print(
        f"[+] Starting ttyd on port {port}"
    )

    subprocess.Popen(command)


# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    threading.Thread(
        target=start_ttyd,
        daemon=True
    ).start()

    port = int(
        os.getenv("PORT", "8080")
    )

    print("=" * 45)
    print("R-BOTS SSH ACCESS")
    print("=" * 45)

    app.run(
        host="0.0.0.0",
        port=port
    )
