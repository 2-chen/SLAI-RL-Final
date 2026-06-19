# Clash-for-Linux Complete Reference

Complete reference for the clash-for-linux VPN/proxy tool installed at `/data/clash-for-linux-install/`.

## Installation

### One-Click Install
```bash
git clone --branch master --depth 1 https://gh-proxy.org/https://github.com/nelvko/clash-for-linux-install.git \
  && cd clash-for-linux-install \
  && bash install.sh
```

### Reinstall
```bash
cd /data/clash-for-linux-install && bash install.sh
```

### Uninstall
```bash
cd /data/clash-for-linux-install && bash uninstall.sh
```

---

## All Commands

| Command | Function | Aliases |
|---------|----------|---------|
| `clashctl on` | Start kernel + set system proxy | `clashon` |
| `clashctl off` | Stop kernel + unset system proxy | `clashoff` |
| `clashctl status` | Show kernel running status | — |
| `clashctl proxy` | Toggle system proxy (keep kernel running) | — |
| `clashctl ui` | Show web dashboard access info | — |
| `clashctl secret [key]` | View or set web dashboard password | — |
| `clashctl sub add <url>` | Add a subscription | — |
| `clashctl sub ls` | List subscriptions | — |
| `clashctl sub del <id>` | Delete a subscription | — |
| `clashctl sub use <id>` | Switch to a subscription | — |
| `clashctl sub update [id]` | Update subscription (fetch latest nodes) | — |
| `clashctl sub log` | View subscription update logs | — |
| `clashctl upgrade` | Upgrade clash/mihomo kernel | — |
| `clashctl tun [on\|off]` | Toggle TUN mode (intercept all traffic) | `clashtun [on\|off]` |
| `clashctl mixin` | View mixin config | `clashmixin` |
| `clashctl mixin -e` | Edit mixin config | `clashmixin -e` |
| `clashctl mixin -c` | View original subscription config | `clashmixin -c` |
| `clashctl mixin -r` | View runtime (merged) config | `clashmixin -r` |

---

## File Paths

| Path | Purpose |
|------|---------|
| `/data/clash-for-linux-install/` | Install directory (git clone) |
| `/data/clash-for-linux-install/.env` | Environment config for install |
| `/data/clash-for-linux-install/install.sh` | Install script |
| `/data/clash-for-linux-install/scripts/cmd/clashctl.sh` | Main control script |
| `/data/clash-for-linux-install/resources/Country.mmdb` | GeoIP database for routing rules |
| `/data/clash-for-linux-install/resources/geosite.dat` | Geo site category data |
| `/data/clash-for-linux-install/resources/mixin.yaml` | Default mixin template |
| `/data/clash-for-linux-install/resources/profiles.yaml` | Default profiles |
| `~/.local/share/clash/` | Runtime directory (config, logs, data) |
| `~/.local/share/clash/config.yaml` | Runtime (merged) configuration |

---

## Default Subscription

```
https://api.eeox.net/api/v1/client/subscribe?token=f55ae0944cde068f2ea27c92f9f7e71d
```

---

## Proxy Environment Variables

When clash is running and system proxy is enabled:

```bash
# HTTP proxy (for http:// URLs)
export http_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890

# HTTPS proxy (for https:// URLs)
export https_proxy=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# SOCKS5 proxy (for all protocols)
export all_proxy=socks5h://127.0.0.1:7890
export ALL_PROXY=socks5h://127.0.0.1:7890

# Bypass proxy for local addresses
export no_proxy=localhost,127.0.0.1,::1
export NO_PROXY=localhost,127.0.0.1,::1
```

The actual port is detected from the runtime config. Default is 7890 (mixed port) but may differ if there was a port conflict during installation.

---

## Port Configuration

Default ports:
- **Mixed port (HTTP + SOCKS)**: 7890
- **Web dashboard**: 9090
- **DNS**: 1053

If the default ports are occupied, the install script auto-assigns random available ports. To find the actual ports:
```bash
clashctl mixin -r | grep -E '(mixed-port|port|socks-port|external-controller)'
```

---

## Web Dashboard

Access the web dashboard (zashboard) at:
- **Internal**: `http://127.0.0.1:9090/ui`
- **LAN**: `http://<lan-ip>:9090/ui`
- **Public**: `http://board.zash.run.place`

Set/view dashboard password:
```bash
clashctl secret           # view current password
clashctl secret mypass    # set to "mypass"
```

---

## Mixin Configuration

Mixin allows customizing the proxy rules by merging your own config with the subscription config. Mixin has highest priority.

```bash
# View current mixin
clashctl mixin

# Edit mixin
clashctl mixin -e

# View original subscription config (before mixin merge)
clashctl mixin -c

# View runtime config (after mixin merge)
clashctl mixin -r
```

### Common Mixin Use Cases

**Add custom proxy rules:**
```yaml
rules:
  - DOMAIN-SUFFIX,openai.com,Proxy
  - DOMAIN-SUFFIX,anthropic.com,Proxy
  - DOMAIN-SUFFIX,huggingface.co,Proxy
  - DOMAIN-SUFFIX,github.com,Proxy
```

**Add custom DNS:**
```yaml
dns:
  enable: true
  nameserver:
    - 223.5.5.5
    - 119.29.29.29
```

---

## TUN Mode

TUN mode creates a virtual network interface that intercepts ALL traffic at the OS level and routes it through the proxy. This includes:
- Docker containers
- System services
- Applications that don't support proxy settings
- UDP traffic

```bash
clashctl tun       # Show TUN status
clashctl tun on    # Enable TUN mode
clashctl tun off   # Disable TUN mode
```

**Warning**: TUN mode affects ALL traffic. Internal/LAN services may become unreachable. Use only when necessary.

---

## Subscription Management

```bash
# Add a subscription
clashctl sub add "https://your-subscription-url"

# Add a local config file
clashctl sub add "file:///path/to/config.yaml"

# List all subscriptions
clashctl sub ls

# Switch to subscription #2
clashctl sub use 2

# Update subscription (fetch latest nodes from server)
clashctl sub update

# Update specific subscription
clashctl sub update 2

# Auto-update subscription daily
clashctl sub update --auto

# Use subscription converter
clashctl sub update --convert

# View subscription logs
clashctl sub log
```

---

## Init System Detection

The install script auto-detects the init system:
- **systemd** → systemd service files
- **SysV init** → init.d scripts
- **AutoDL / container** → environment-level setup

---

## Troubleshooting Quick Reference

| Issue | Check | Fix |
|-------|-------|-----|
| `clashctl: command not found` | Not installed or not in PATH | Reinstall: `cd /data/clash-for-linux-install && bash install.sh` |
| Kernel not starting | Port conflict or config error | `clashctl mixin -r` to check config; `lsof -i :7890` to check port |
| Proxy vars not set in new shell | Shell rc not sourced | Run `clashon` or `source <(clashctl proxy)` in the new shell |
| Sites blocked even with proxy | Wrong node or expired subscription | `clashctl sub update`; switch node via web dashboard |
| Slow speed | Node congested or far away | Switch to a closer/faster node in web dashboard |
| Docker can't access internet | Docker bypasses system proxy | Enable TUN mode (`clashctl tun on`) |
| pip/git/conda not using proxy | These tools have their own proxy config | Set per-tool proxy config (see SKILL.md diagnosis table) |
| Subscription URL fails | Token expired or server down | Get a new subscription URL |
| Web dashboard can't open | Port blocked or wrong port | Check actual port: `clashctl mixin -r \| grep external` |

---

## Architecture

```
┌──────────────────────────────────────────────┐
│              Clash-for-Linux                   │
│                                                 │
│  ┌──────────┐    ┌──────────────┐              │
│  │ Subscription│──→│ subconverter │             │
│  │  (remote)  │    │  (optional)  │             │
│  └──────────┘    └──────┬───────┘              │
│                          │                      │
│                          ↓                      │
│                   ┌──────────────┐              │
│                   │  mixin.yaml  │              │
│                   │  (user rules)│              │
│                   └──────┬───────┘              │
│                          │                      │
│                          ↓                      │
│              ┌───────────────────┐              │
│              │  Runtime Config   │              │
│              │  (merged YAML)    │              │
│              └────────┬──────────┘              │
│                       │                         │
│                       ↓                         │
│              ┌───────────────────┐              │
│              │  mihomo kernel    │              │
│              │  (proxy engine)   │              │
│              └────────┬──────────┘              │
│                       │                         │
│         ┌─────────────┼─────────────┐           │
│         ↓             ↓             ↓           │
│    HTTP:7890    SOCKS5:7890    Dashboard:9090  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  System Proxy (env vars)                  │  │
│  │  http_proxy=https_proxy=all_proxy=...     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  TUN Mode (optional)                      │  │
│  │  Virtual NIC intercepts all traffic       │  │
│  └──────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

---

## Subscription Flow

1. User adds a subscription URL (remote server or local file)
2. Clash periodically fetches the subscription → downloads proxy node list + rules
3. If `--convert` is used, the subscription is processed through subconverter (local binary) to convert between formats (e.g., Shadowsocks → Clash)
4. Mixin config is deep-merged with subscription config (mixin has highest priority)
5. Final merged config is written to `~/.local/share/clash/config.yaml`
6. mihomo kernel loads the runtime config and starts proxying
