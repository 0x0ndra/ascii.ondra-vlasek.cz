# Deployment Guide

Generic guide for running the web interface on your own server. The live deployment of
ascii.ondra-vlasek.cz is described in [DEPLOYMENT.md](DEPLOYMENT.md).

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Install dependencies: `pip install -r requirements.txt` (in a venv)
4. Run: `set -a; . ./.env; set +a; python3 web_interface.py`

The app does not load `.env` by itself, it only reads `SERVER_HOST` and `SERVER_PORT` from the
process environment. Without them it binds to `0.0.0.0:7860`.

## Production Deployment

### Using Systemd

Run the app as a dedicated system user without a login shell and bind it to localhost only
(`SERVER_HOST=127.0.0.1` in `.env`), so that it is reachable only through nginx.

1. Create service file in `/etc/systemd/system/ascii-photo-mask.service`:
```ini
[Unit]
Description=ASCII Photo Mask Web Interface
After=network.target

[Service]
Type=simple
User=YOUR_APP_USER
Group=YOUR_APP_USER
WorkingDirectory=/path/to/ascii-photo-mask
Environment="PATH=/path/to/venv/bin"
EnvironmentFile=/path/to/ascii-photo-mask/.env
ExecStart=/path/to/venv/bin/python3 /path/to/ascii-photo-mask/web_interface.py
Restart=always
RestartSec=10
PrivateTmp=yes
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes

[Install]
WantedBy=multi-user.target
```

The app writes only temporary files (uploads and generated PNGs) to `/tmp`, so with
`PrivateTmp=yes` it needs no other writable path.

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ascii-photo-mask
```

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then test and reload: `sudo nginx -t && sudo systemctl reload nginx`.

### SSL with Certbot

```bash
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

- `SERVER_HOST` - Host to bind (default: 0.0.0.0, use 127.0.0.1 behind nginx)
- `SERVER_PORT` - Port to listen (default: 7860)
