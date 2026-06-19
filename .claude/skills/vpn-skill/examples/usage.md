# VPN Skill — Usage Examples

## Example 1: Basic Turn On

**User:**
```
Turn on VPN
```

**Skill executes:**
1. `clashctl status` → reports "not running"
2. `clashon` → starts kernel + sets proxy env vars
3. Test: `curl -s --max-time 10 https://huggingface.co` → 200
4. Report: "VPN enabled. Proxy at http://127.0.0.1:7890. All key sites reachable."

## Example 2: Turn Off

**User:**
```
Turn off VPN
```

**Skill executes:**
1. `clashoff` → stops kernel + unsets proxy env vars
2. Verify: `env | grep -i proxy` → empty
3. Report: "VPN disabled. Direct network access restored."

## Example 3: Check Status

**User:**
```
How's my VPN? Is it working?
```

**Skill executes:**
1. `clashctl status` → "running (pid 12345)"
2. Check env vars → all proxy vars set to http://127.0.0.1:7890
3. Test connectivity:
   - Baidu: 200 ✓
   - HuggingFace: 200 ✓
   - GitHub: 200 ✓
   - arXiv: 200 ✓
4. Display status dashboard

## Example 4: Diagnose Download Failure

**User:**
```
I'm trying to download a model from HuggingFace but it's stuck. What's wrong?
```

**Skill executes:**
1. `clashctl status` → running ✓
2. `env | grep proxy` → no proxy vars set ✗
3. Diagnosis: "Proxy kernel is running but system proxy env vars are not set in this shell session."
4. Fix: `source <(clashctl proxy)` to re-export vars
5. Retry HF download → works
6. Report: "The proxy kernel was running but this shell didn't have the proxy env vars. Fixed — HF downloads should work now."

## Example 5: Network Error from Another Skill (search-skill)

**User (to search-skill):**
```
Search papers on "diffusion models for protein design"
```

**search-skill encounters:**
```
curl: (7) Failed to connect to api.semanticscholar.org port 443: Connection timed out
```

**search-skill auto-invokes vpn-skill:**
1. vpn-skill detects pattern: "Connection timed out"
2. `clashctl status` → not running
3. `clashon` → proxy enabled
4. Test connectivity → all sites reachable
5. Return to search-skill: "Network fixed. Retry your search."

**search-skill retries → succeeds**

## Example 6: pip Install Behind Proxy

**User:**
```
I need to pip install torch-geometric but pip keeps timing out
```

**Skill executes:**
1. `clashctl status` → running
2. `env | grep proxy` → proxy vars set
3. Test: `pip install --dry-run torch-geometric 2>&1 | head` → timeout
4. Diagnosis: pip may use its own connection pool. Explicitly check `https_proxy`.
5. Run with explicit proxy:
   ```bash
   HTTPS_PROXY=http://127.0.0.1:7890 pip install torch-geometric
   ```
6. Success

## Example 7: git clone Large Repo

**User:**
```
git clone https://github.com/facebookresearch/llama.git is super slow
```

**Skill executes:**
1. Check proxy status → running, env vars set
2. Diagnosis: git doesn't automatically use HTTP_PROXY for https:// URLs
3. Fix:
   ```bash
   git config --global http.proxy http://127.0.0.1:7890
   git clone https://github.com/facebookresearch/llama.git
   git config --global --unset http.proxy  # clean up after
   ```
4. Clone succeeds at normal speed

## Example 8: TUN Mode for Docker

**User:**
```
My Docker container can't access the internet. I need it to go through the proxy.
```

**Skill executes:**
1. Warn: "TUN mode intercepts ALL network traffic at the interface level. Docker containers and all processes will be routed through the proxy. Proceed?"
2. User confirms
3. `clashctl tun on`
4. Verify: run a test container with `curl huggingface.co` → succeeds
5. Report: "TUN mode enabled. All traffic (including Docker) now routes through the proxy."

## Example 9: Subscription Update

**User:**
```
My VPN seems slow or some sites don't work. Update the subscription.
```

**Skill executes:**
1. `clashctl sub update` → updates proxy node list
2. If needed, switch to a better node via web dashboard: `clashctl ui`
3. Test connectivity with the updated nodes
4. Report: "Subscription updated. If speed is still slow, try switching nodes in the web dashboard."

## Example 10: Setup from Scratch

**User:**
```
Set up VPN on this machine
```

**Skill executes:**
1. Check if `/data/clash-for-linux-install/` exists → yes
2. Run `bash install.sh` from that directory
3. Add subscription automatically
4. `clashon` → start proxy
5. Test connectivity → all green
6. Report: "VPN installed and running. Proxy at http://127.0.0.1:7890"
