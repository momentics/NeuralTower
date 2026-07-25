# Software Stack Overview

## Boot-to-Inference Route

The NeuralTower software stack follows a deterministic path from hardware initialization to model inference:

1. **BIOS Configuration** — Above 4G Decoding, forced PCIe Gen3, UEFI mode (see [bios-settings.md](../05-hardware/bios-settings.md))
2. **Linux and Drivers** — Gentoo with kernel parameters `pci=realloc,assign-busses pci=hp_pcie_bus_max`, NVIDIA driver with `uvm`, all 4 GPUs visible (see [system-setup.md](./system-setup.md))
3. **Gentoo Optimization** — Broadwell-optimized compilation, hugepages, NUMA tuning (see [gentoo-config.md](./gentoo-config.md))
4. **ML Environment Build** — CUDA 12.8, Python 3.12, PyTorch cu128, vLLM/SGLang installation (see [world-build.md](./world-build.md))
5. **Inference Engine** — 1Cat-vLLM or SGLang with TP=2 + PP=2 topology (see [vllm.md](./vllm.md) or [sglang/README.md](./sglang/README.md))
6. **Monitoring** — Grafana dashboard + GPU Watchdog (see [monitoring.md](./monitoring.md))

## Inference Engine Paths

### Path A: 1Cat-vLLM (Recommended)

Fork with restored V100 support, FlashAttention-2 for sm_70, and AWQ 4-bit quantization. Pre-built wheel packages for CUDA 12.8 + Python 3.12.

### Path B: Official vLLM 0.18.x (Alternative)

Last official release with native sm_70 support. Uses Triton JIT kernels. Slower than FlashAttention-2 but stable.

> Official vLLM 0.20+ dropped sm_70 support entirely (CUDA 13.0, PyTorch 2.11+). Not usable on V100.

### Path C: SGLang (Alternative)

Three-level HiCache (GPU HBM → CPU RAM → NVMe SSD), RadixAttention context reuse, and EAGLE/MTP speculative decoding. See [sglang/README.md](./sglang/README.md).

## Key Constraints

| Constraint | Value | Reason |
|-----------|-------|--------|
| GPU Architecture | V100 sm_70 | Volta architecture, 2017 |
| CUDA Version | 12.8 | Last stable version with full sm_70 support |
| Precision | FP16 only | BF16 emulated (slow), FP8/MXFP4 unavailable (requires sm_80+) |
| Python | 3.12 | Required for 1Cat-vLLM pre-built wheels |
| GPU Memory | 32 GB per GPU (128 GB total) | V100 SXM2-32G |

## Kernel Profiles

The system supports two kernel profiles selectable at boot via GRUB:

- **Performance** — maximum KV-cache throughput, no security mitigations
- **Hardened** — KASLR, stack protection, lockdown mode

See [profiles.md](./profiles.md) for build instructions.

## Related Documents

| File | Description |
|------|-------------|
| [system-setup.md](./system-setup.md) | Route from power-on to first model run |
| [gentoo-config.md](./gentoo-config.md) | Gentoo optimization for vLLM and SGLang |
| [world-build.md](./world-build.md) | Reproducible Python/CUDA/PyTorch/vLLM installation |
| [vllm.md](./vllm.md) | vLLM optimization, TP/PP, NCCL, NVMe swap |
| [sglang/README.md](./sglang/README.md) | SGLang deployment with Prometheus/Grafana |
| [monitoring.md](./monitoring.md) | Grafana dashboard and GPU Watchdog |
| [profiles.md](./profiles.md) | Performance and Hardened kernel profiles |
