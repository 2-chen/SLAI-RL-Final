# SCO Configuration Reference (2chen)

Complete reference for SCO ACP job submission parameters used by sco-skill.

## Workspace & Cluster

| Parameter | Value | Notes |
|-----------|-------|-------|
| Workspace | `share-space` | Shared workspace in cn-sh-01g zone |
| Cluster | `share-cluster` | AEC2 cluster, zone cn-sh-01g |
| SCO config zone | `cn-sh-01g` | Must match workspace/cluster zone |

Verify connectivity:
```bash
sco config list
sco aec2 clusters list
sco aec2 clusters describe --name share-cluster
```

## Container Image

Default image: `registry.cn-sh-01.sensecore.cn/ccr-zhicheng-02/chen-mirror2:2chen-mini-20260410132739`

This is a minimal PyTorch image. To check available images:
```bash
sco ccr images list
sco ccr images list -p  # paginated
```

To build a custom image:
```bash
sco ccr builds create -n <namespace> -f ./Dockerfile -t <tag> -c ./context
```

## Worker Specs

Default: `n6ls.iu.i40.4.32c512g` (4× NVIDIA N6LS-80G-SXM5, 32 vCPU, 512GB RAM)

List available worker specs:
```bash
sco aec2 clusters list-workerspec --workspace-name share-space --aec2-name share-cluster
```

Common specs:
| Spec | GPUs | vCPU | RAM | GPU Type |
|------|------|------|-----|----------|
| `n6ls.iu.i40.4.32c512g` | 4 | 32 | 512GB | N6LS-80G-SXM5 |
| `n6ls.iu.i40.8.64c1024g` | 8 | 64 | 1024GB | N6LS-80G-SXM5 |

## Storage Mount

Default AFS volume: `afs-share-01g`
Volume ID: `01995892-d478-76d8-aec7-13fd8284477e`
Mount format: `<volume_id>:<container_path>:<afs_subdirectory>`
Default: `01995892-d478-76d8-aec7-13fd8284477e:/data:/250010008`

This maps:
- Container path `/data` → AFS directory `/250010008`

AFS operations:
```bash
sco afs volume list
sco afs volume list -i 01995892-d478-76d8-aec7-13fd8284477e
sco afs volume ls -i 01995892-d478-76d8-aec7-13fd8284477e -d /250010008
sco afs dir-quota list -i 01995892-d478-76d8-aec7-13fd8284477e
```

AFS base path for experiments: `/data/250010008/chenresearch`

## Quota Types

| Type | Flag | Behavior |
|------|------|----------|
| Reserved | `--quota-type reserved` | Standard reserved quota, guaranteed resources |
| Spot | `--quota-type spot` | Preemptible/idle resources, may be interrupted |

Default: `reserved`. Only use `spot` when user explicitly requests it.

## Priority Levels

| Priority | Flag | Use Case |
|----------|------|----------|
| Normal | `--priority normal` | Standard experiments (default) |
| High | `--priority high` | Time-sensitive experiments |
| Highest | `--priority highest` | Critical/urgent jobs |

## Full Submit Command Reference

```bash
sco acp jobs create \
  --workspace-name share-space \
  --aec2-name share-cluster \
  --job-name "<job_name>" \
  --container-image-url "registry.cn-sh-01.sensecore.cn/ccr-zhicheng-02/chen-mirror2:2chen-mini-20260410132739" \
  --training-framework pytorch \
  --worker-nodes 1 \
  --worker-spec n6ls.iu.i40.4.32c512g \
  --priority normal \
  --quota-type reserved \
  --storage-mount 01995892-d478-76d8-aec7-13fd8284477e:/data:/250010008 \
  --command "<remote_command>"
```

Optional flags:
- `--env key:value,...` — set environment variables in container
- `--enable-fault-tolerance` — auto-restart on node failure
- `--retry-times N` — max retry attempts
- `--follow` — stream logs after submission

## Job Management Commands

```bash
# List recent jobs
sco acp jobs list --workspace-name share-space --page-size 20 -o table

# Describe a job (get status, workers, etc.)
sco acp jobs describe --workspace-name share-space -o json <job_id>

# Get worker names for a job
sco acp jobs get-workers --workspace-name share-space <job_id>

# Stream logs
sco acp jobs stream-logs --workspace-name share-space <job_id>
sco acp jobs stream-logs --workspace-name share-space <job_id> --follow

# Execute command in running job
sco acp jobs exec --workspace-name share-space --worker-name <worker> <job_id>

# Control
sco acp jobs stop --workspace-name share-space <job_id>
sco acp jobs start --workspace-name share-space <job_id>
sco acp jobs delete --workspace-name share-space <job_id>
```

## Job Status States

| State | Meaning |
|-------|---------|
| PENDING | Queued, waiting for resources |
| PULLING | Pulling container image |
| RUNNING | Actively executing |
| SUCCEEDED | Completed successfully (exit code 0) |
| FAILED | Completed with error (exit code ≠ 0) |
| STOPPED | Manually stopped by user |
| CANCELLED | Cancelled by system or user |

Terminal states: `SUCCEEDED`, `FAILED`, `STOPPED`, `CANCELLED`

## Remote Command Construction

The remote command runs inside the container. ACP 和 CCI 的 `/data/` 存储是共享的，所以脚本在容器内可以直接访问原始路径，无需复制。

Pattern:

```bash
set -euo pipefail
cd <script_directory>     # 脚本所在目录（/data/ 下原路径）
export VAR1=value1
export VAR2=value2
bash <script_name>.sh     # 脚本文件名
```

Example — 跑 `/data/homework/RL/final/launch_ood_4gpu.sh`：

```bash
set -euo pipefail
cd /data/homework/RL/final
bash launch_ood_4gpu.sh
```

Key rules:
- Always `set -euo pipefail` for strict error handling
- `cd` 到脚本所在目录（ACP 容器内可直接访问 `/data/` 下的任意路径）
- 直接 `bash <script>`，不硬编码文件名
- Export any needed environment variables before running the script
- Keep the command simple — the script handles everything else
- 仅当脚本不在 `/data/` 下时才复制到 `/data/250010008/chenresearch/`
