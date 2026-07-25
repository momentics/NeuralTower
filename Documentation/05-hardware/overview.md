# Hardware Preparation

This section covers the hardware preparation for the NeuralTower system, including GPU preparation and BIOS configuration for the four Tesla V100 SXM2 accelerators on the LGA 2011-3 desktop platform.

## GPU Preparation Summary

The Tesla V100 SXM2 modules require removal of factory radiators, cleaning of GPU and HBM2 memory dies, and installation of Speedier XF-001-CO water blocks (140 x 80 x 30 mm, 300W TDP). Proper thermal interface material selection and uniform clamping pressure are critical for long-term reliability.

## BIOS Settings Summary

| Parameter | Path in BIOS | Value |
| --- | --- | --- |
| Above 4G Decoding | Advanced → PCI Subsystem Settings → Above 4G Decoding | Enabled |
| PCIEX16_1-7 Link Speed | Advanced → System Agent Configuration → NB PCI-E Configuration | Gen3 |
| PCIe Speed | Advanced → CPU Configuration → PCI Express Configuration → PCIe Speed | Gen3 |
| Intel VT-d | Advanced → System Agent Configuration → Intel VT-d | Disabled |
| CPU states | Advanced → CPU Configuration → CPU Power Management Configuration | Disabled |
| Package C State Support | Advanced → CPU Configuration → CPU Power Management Configuration | C0/C1 |
| Launch CSM | Boot → Boot Configuration → CSM → Launch CSM | Disabled |
| OS Type | Boot → Boot Configuration → Secure Boot → OS Type | Other OS |

## Detailed Guides

- [GPU Preparation](./gpu-preparation.md) — Disassembly, water block installation, and mezzanine integration
- [BIOS Settings](./bios-settings.md) — Full BIOS configuration and system logic optimization
