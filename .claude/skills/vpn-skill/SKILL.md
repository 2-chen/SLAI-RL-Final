---
name: vpn-skill
description: "VPN/proxy management skill — wraps clash-for-linux (mihomo kernel) to enable/disable proxy, check status, manage subscriptions, and provide network access for downloading models, datasets, papers, and other resources blocked by network restrictions. 6 modes: on, off, status, setup, diagnose, full. Triggers on: vpn, proxy, network, 翻墙, clash, 网络, 代理, download blocked, network error, cannot connect, connection refused, timeout, GFW."
metadata:
  version: "1.0"
  last_updated: "2026-05-29"
  depends_on: "clash-for-linux (mihomo kernel)"
---

# VPN Skill — Network Proxy Management

Manages the clash-for-linux proxy tool to provide reliable network access for research tasks. When other skills encounter network errors (download failures, connection timeouts, blocked hosts), this skill is invoked to enable proxy access. It is a **supporting skill** — it does not do research itself but ensures other skills can reach the external resources they need.

## Quick Start

**Enable proxy:**
```
Turn on VPN
```

**Disable proxy:**
```
Turn off VPN
```

**Check status:**
```
Check VPN status
```

**Diagnose network issue:**
```
I can't download from HuggingFace — diagnose the network
```

**Execution flow:**
1. Diagnose: check if proxy is running and system proxy is set
2. Fix: start proxy if needed, set environment variables
3. Verify: test connectivity to blocked targets
4. Report: confirm network is working

---

## Trigger Conditions

### Trigger Keywords

**English**: vpn, proxy, clash, network issue, network error, network problem, turn on proxy, enable proxy, start proxy, turn off proxy, disable proxy, stop proxy, check proxy, proxy status, download blocked, cannot download, connection refused, connection timeout, cannot connect, GFW, blocked site, huggingface blocked, github blocked, google blocked, need proxy, network access, 翻墙, 代理, 网络, 网络问题, 梯子

**Traditional Chinese**: 翻牆, 代理, 網絡, 網絡問題, VPN, 梯子, 科學上網

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| SCO experiment submission | `experiment-skill` |
| Paper/literature search | `search-skill` |
| Paper writing | `write-skill` |
| Peer review | `review-skill` |
| Model inference (not network-related) | Whatever skill handles it |

### Auto-Invocation by Other Skills

Other skills MAY auto-invoke `vpn-skill` when they encounter network errors:

| Error Pattern | Action |
|---------------|--------|
| `Connection refused`, `Connection timeout`, `Name resolution failed` | Call VPN skill → diagnose → enable proxy → retry |
| `403`, `429` from huggingface.co / github.com | Call VPN skill → enable proxy → retry |
| `Could not resolve host`, `Temporary failure in name resolution` | Call VPN skill → enable proxy → retry |
| `curl: (7) Failed to connect`, `wget: network is unreachable` | Call VPN skill → enable proxy → retry |
| Socket timeout, SSL handshake timeout | Call VPN skill → enable proxy → retry |

---

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| `on` | "turn on VPN", "enable proxy", "start clash" | Start clash kernel + set system proxy env vars |
| `off` | "turn off VPN", "disable proxy", "stop clash" | Stop clash kernel + unset system proxy env vars |
| `status` | "check VPN", "proxy status" | Report kernel status, proxy settings, connection test |
| `setup` | "install clash", "setup VPN" | Install/reinstall clash-for-linux from /data/clash-for-linux-install/ |
| `diagnose` | "diagnose network", "why can't I download" | Check proxy health, test connectivity, identify issues |
| `full` | "fix network", "get online" | diagnose → on (if needed) → verify → report |

Default mode: `on` (when user says "turn on VPN") or `diagnose` (when user reports a network error).

---

## Architecture

### What Clash-for-Linux Does

The VPN tool at `/data/clash-for-linux-install/` provides:

1. **Clash/mihomo kernel** — a proxy client that connects to remote proxy servers via subscription
2. **System proxy** — sets `http_proxy`, `https_proxy`, `all_proxy` environment variables
3. **TUN mode** — optional, routes all traffic through the proxy at the network interface level
4. **Web dashboard** — visual management of proxy nodes and rules

### Key Files

| Path | Purpose |
|------|---------|
| `/data/clash-for-linux-install/` | Install directory (clone of the tool) |
| `/data/clash-for-linux-install/install.sh` | One-click install script |
| `/data/clash-for-linux-install/scripts/cmd/clashctl.sh` | Main control script (sourced by clashctl) |
| `~/.local/share/clash/` | Clash configuration and runtime files |
| `~/.local/share/clash/config.yaml` | Runtime clash configuration |

### Commands Reference

All commands from the README:

```bash
# Start/stop proxy
clashon                    # Enable proxy (alias for clashctl on)
clashoff                   # Disable proxy (alias for clashctl off)

# Full command set
clashctl on                # Enable proxy kernel + system proxy
clashctl off               # Disable proxy kernel + system proxy
clashctl status            # Check kernel running status
clashctl proxy             # Toggle system proxy only (without stopping kernel)
clashctl ui                # Open web dashboard info
clashctl secret [key]      # Set/view web dashboard access key
clashctl sub               # Subscription management (add/ls/del/use/update)
clashctl upgrade           # Upgrade clash/mihomo kernel
clashctl tun [on|off]      # TUN mode (intercept all traffic)
clashctl mixin             # View/edit mixin config (merge with subscription)
```

---

## Mode: on — Enable Proxy

### Workflow

1. Check if clash kernel is already running via `clashctl status`
2. If not running, start it:
   ```bash
   clashon
   ```
   (This starts the mihomo kernel AND sets system proxy environment variables)
3. Verify proxy environment variables are set:
   ```bash
   env | grep -i proxy
   ```
   Expected: `http_proxy`, `https_proxy`, `HTTP_PROXY`, `HTTPS_PROXY`, `all_proxy`, `ALL_PROXY` should all be set
4. Test connectivity to a common blocked site:
   ```bash
   curl -s --max-time 10 https://huggingface.co -o /dev/null -w "%{http_code}"
   ```
   - `200` or `302` → proxy working ✓
   - `000` or timeout → proxy may not be working, proceed to diagnose
5. Report status to user

### Environment Variables Set

When proxy is enabled, these are set in the current shell:
```
http_proxy=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
all_proxy=socks5h://127.0.0.1:7890
no_proxy=localhost,127.0.0.1,::1
```

**Important**: These only affect the current shell session. When launching a new shell, the proxy settings may not be inherited unless `clashon` was called with the shell's rc file sourced.

### For Subprocesses (curl, wget, pip, git, huggingface_hub)

When running tools that need proxy access, explicitly export the proxy variables before use:
```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export all_proxy=socks5h://127.0.0.1:7890
# Then run the command:
curl -L -O https://huggingface.co/datasets/.../resolve/main/data.zip
```

Or use proxychains if TUN mode is not available:
```bash
proxychains4 curl -L -O https://...
```

---

## Mode: off — Disable Proxy

### Workflow

1. Stop clash kernel and unset system proxy:
   ```bash
   clashoff
   ```
   (This stops the mihomo kernel and unsets all proxy environment variables)
2. If only system proxy needs to be toggled (keep kernel running), use:
   ```bash
   clashctl proxy
   ```
3. Verify no proxy variables remain:
   ```bash
   env | grep -i proxy || echo "No proxy set — clean"
   ```
4. Test direct connectivity:
   ```bash
   curl -s --max-time 10 https://www.baidu.com -o /dev/null -w "%{http_code}"
   ```

---

## Mode: status — Check Proxy Status

### Workflow

1. Check kernel status:
   ```bash
   clashctl status
   ```
2. Check system proxy environment:
   ```bash
   env | grep -i proxy
   ```
3. Test connectivity to both domestic and international sites:
   ```bash
   # Domestic (should work without proxy)
   curl -s --max-time 5 https://www.baidu.com -o /dev/null -w "Baidu: %{http_code}\n"
   # International (needs proxy in China)
   curl -s --max-time 5 https://huggingface.co -o /dev/null -w "HuggingFace: %{http_code}\n"
   curl -s --max-time 5 https://github.com -o /dev/null -w "GitHub: %{http_code}\n"
   curl -s --max-time 5 https://arxiv.org -o /dev/null -w "arXiv: %{http_code}\n"
   ```
4. Report:
   ```
   ╔══════════════════════════════════╗
   ║       VPN Status Report          ║
   ╠══════════════════════════════════╣
   ║ Kernel:     running ✓            ║
   ║ HTTP Proxy: http://127.0.0.1:7890║
   ║ SOCKS:      socks5://127.0.0.1:7890║
   ║ Baidu:      200 ✓                ║
   ║ HuggingFace: 200 ✓               ║
   ║ GitHub:     200 ✓                ║
   ║ arXiv:      200 ✓                ║
   ╚══════════════════════════════════╝
   ```

---

## Mode: setup — Install/Reinstall VPN

### Workflow

1. Check if `/data/clash-for-linux-install/install.sh` exists
2. Run installation:
   ```bash
   cd /data/clash-for-linux-install && bash install.sh
   ```
   This will:
   - Detect system architecture and init system
   - Download the appropriate mihomo/clash kernel
   - Install the `clashctl` command and shell aliases (`clashon`, `clashoff`)
   - Set up service management (systemd or equivalent)
   - Generate default configuration
3. After install, add subscription:
   ```bash
   clashctl sub add https://api.eeox.net/api/v1/client/subscribe?token=f55ae0944cde068f2ea27c92f9f7e71d
   clashctl sub use 1
   ```
4. Verify by running `clashon` and testing connectivity

### Pre-requisites

- The install directory at `/data/clash-for-linux-install/` must exist (git cloned)
- `bash` and `curl` must be available
- The subscription URL must be valid

### Customization via .env

The install script reads `/data/clash-for-linux-install/.env` for custom settings:
```bash
# Example .env
CLASH_BASE_DIR=~/.local/share/clash
CLASH_CONFIG_URL=file:///data/clash-for-linux-install/resources/profiles.yaml
```

---

## Mode: diagnose — Network Troubleshooting

### Workflow

1. Check current proxy state:
   - Is clash kernel running? (`clashctl status`)
   - Are proxy env vars set? (`env | grep proxy`)
   - What ports is clash listening on?
2. Test connectivity step by step:
   ```bash
   # Step 1: localhost proxy reachable?
   curl -s --max-time 3 http://127.0.0.1:7890 -o /dev/null -w "Local proxy: %{http_code}\n"
   
   # Step 2: DNS resolution works?
   nslookup huggingface.co 2>&1 | head -5
   
   # Step 3: HTTP to international site via proxy?
   curl -s --max-time 10 --proxy http://127.0.0.1:7890 https://huggingface.co -o /dev/null -w "HuggingFace(via proxy): %{http_code}\n"
   ```
3. Identify the failure point:
   | Symptom | Likely Cause | Fix |
   |---------|-------------|-----|
   | `clashctl status` shows "not running" | Kernel crashed or never started | Run `clashon` |
   | Proxy env vars missing | Shell session doesn't have proxy set | Run `source <(clashctl proxy)` or start new shell with `clashon` |
   | `127.0.0.1:7890` unreachable | Wrong port or kernel not listening | Check `clashctl mixin -r` for actual port |
   | DNS resolution fails | DNS not routed through proxy | Use TUN mode (`clashctl tun on`) or set `https_proxy` for DNS |
   | 403/rate limited via proxy | Proxy node IP flagged | Switch node via web dashboard (`clashctl ui`) |
   | Subscription expired | Subscription token expired | Update subscription (`clashctl sub update`) |
4. Output diagnostic report with specific fix actions

### Common Failure Patterns

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| `pip install` timeout | PyPI not routed through proxy | `export https_proxy=http://127.0.0.1:7890 && pip install ...` |
| `git clone` very slow or stuck | Git protocol not proxied | Use `https://` URL or set `http.proxy`: `git config --global http.proxy http://127.0.0.1:7890` |
| `huggingface_hub` download fails | HF hub uses its own HTTP client | Set `HF_ENDPOINT=https://hf-mirror.com` or export proxy vars before Python |
| `curl` / `wget` to GitHub returns 403 | GitHub blocks non-browser requests | Use `--header "User-Agent: ..."` or enable proxy |
| `conda install` fails | Conda doesn't respect system proxy | Set in `.condarc`: `proxy_servers: {http: http://127.0.0.1:7890, https: http://127.0.0.1:7890}` |

---

## Mode: full — Fix and Verify

Execute sequentially: diagnose → on (if needed) → verify connectivity → report.

```
1. diagnose — identify the issue
2. If kernel not running → clashon
3. If proxy env vars missing → re-export them
4. If subscription expired → clashctl sub update
5. Test connectivity to all key sites
6. Report: "Network is ready. Proxy active on http://127.0.0.1:7890"
```

---

## Integration with Other Skills

The VPN skill is designed to be called by other skills when they hit network errors.

### search-skill
- **When**: arXiv API, Semantic Scholar API, or PDF download returns connection errors
- **Action**: `vpn-skill on` → retry search/download → `vpn-skill off` (optional, if user prefers)

### experiment-skill
- **When**: `pip install` inside experiment script fails due to network; container image pull fails
- **Action**: Inject proxy env vars into remote command or use proxychains

### write-skill
- **When**: LaTeX package download fails, bibliography fetching fails
- **Action**: `vpn-skill on` → retry downloads

### review-skill
- **When**: paperreview.ai submission or polling times out
- **Action**: `vpn-skill on` → retry API calls

### pipeline-skill
- **When**: Any stage fails with network errors; model/dataset downloads blocked; paper submission unreachable
- **Action**: Auto-invoke `vpn-skill full` before retrying the failed stage

---

## Safety Rules

1. **Don't leave proxy on for SCO jobs**: The SCO cluster has its own network (inside SenseCore). Proxy settings may interfere with internal services. Always unset proxy in remote commands unless explicitly needed.
2. **Check before enabling**: If proxy is already working, don't restart — just confirm it's operational.
3. **Don't expose proxy port publicly**: The web dashboard on port 9090 should not be exposed to the public internet. Use SSH port forwarding for remote access.
4. **Subscription privacy**: The subscription URL contains a token. Don't log it or include it in any output visible to others.
5. **TUN mode caution**: TUN mode intercepts ALL traffic at the network interface. Only enable when explicitly needed (e.g., Docker containers need proxy).
6. **Verify after enabling**: Always test connectivity to the target service before reporting success.
7. **NetworkDiagnostics for Claude Code**: If the user is on a network that blocks Anthropic's API, the VPN can't help Claude Code itself — it's the user's client that needs the proxy. Instructions for that: set `http_proxy` before launching Claude Code.

---

## Reference Loading

- Read [clash_reference.md](references/clash_reference.md) for complete clash command reference, configuration paths, and troubleshooting
