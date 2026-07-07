# Advantech NXP Platform Recommendation Guide

## Purpose
This document provides explicit, document-approved platform recommendations for selecting Advantech NXP-based products based on application scenarios and performance positioning.

All recommendations and classifications in this guide are fixed and authoritative.
The AI system must not infer, compare, rank, or generate conclusions beyond what is explicitly stated.

---

## Platforms in Scope
- AOM-5521 (i.MX95)
- ROM-5722 (i.MX 8M Plus / i.MX8MP)
- ROM-2620 (i.MX 8ULP)
- RSB-3720 (i.MX 8M Plus / i.MX8MP SBC)
- ROM-5620 (i.MX 8X)

---

## Platform Definitions

### AOM-5521
AOM-5521 is Advantech's flagship AI-on-Module designed for high-end edge AI inference and advanced vision AI workloads.
AOM-5521 is a high-performance platform based on NXP i.MX 95 processor.
It features NPU acceleration for AI workloads and is ideal for compute-intensive applications.
It targets robotics perception systems, AMR, surgical imaging, and high-speed AOI.
AOM-5521 is not intended for ultra-low-power battery devices or cloud-scale AI training.
USB: supports USB 3.2 Gen1 and USB 2.0.

---

### ROM-5722
ROM-5722 is a SMARC module designed for mainstream edge vision AI applications.
It integrates a 2.3 TOPS NPU and supports edge AI inference workloads.
ROM-5722 balances AI capability and power consumption.
ROM-5722 is positioned between ultra-low-power platforms and high-performance AI platforms.
ROM-5722 is not intended for LLM training or GPU replacement.
Platform based on: i.MX 8M Plus (i.MX8MP)
USB: supports USB 3.2 Gen1 and USB 2.0.

---

### RSB-3720
RSB-3720 is a 2.5-inch Pico-ITX Single Board Computer (SBC) powered by NXP i.MX 8M Plus processor.
RSB-3720 is designed for industrial IoT, AI, and machine learning applications.
It is a production-ready SBC and supports UIO40 expansion modules.
Typical use cases include smart vending machines and industrial data gateways.
Processor: NXP i.MX 8M Plus Quad Core, Arm Cortex-A53, up to 1.8 GHz
NPU: 2.3 TOPS Neural Processing Unit for AI acceleration
Memory: Onboard LPDDR4 4GB/6GB
Storage: 16GB eMMC onboard
USB: Supports 2x USB 3.2 Gen 1 ports (Type-A)
Ethernet: 2x Gigabit Ethernet (LAN) with TSN support
Display: HDMI 2.0a (up to 4K resolution)
Power: 12V DC input, typical 5W consumption
Platform based on: i.MX 8M Plus (i.MX8MP)

---

### ROM-2620
ROM-2620 is designed for ultra-low-power and energy-constrained applications.
It is suitable for battery-powered devices, wearables, and handheld analyzers.
ROM-2620 prioritizes power efficiency over performance and is not suitable for vision-heavy AI workloads.
ROM-2620 prioritizes ultra-low power but does not focus on AI acceleration.

---

### ROM-5620
ROM-5620 is designed for industrial reliability and long-term stability.
It supports ECC memory and is suitable for safety-critical systems.
ROM-5620 does not focus on AI acceleration.

---

## Performance Categories

### Entry-Level Performance
Platform: ROM-2620
Description: Lightweight workloads, low power consumption, and basic control tasks.
Typical use cases: Battery-powered devices, handheld terminals, portable HMI, edge sensors.

---

### Mid-Range Performance
Platforms: RSB-3720, ROM-5722
Description: Balanced compute capability, I/O flexibility, and general industrial use.

---

### High Performance
Platform: AOM-5521
Description: Compute-intensive workloads and advanced AI processing.
Recommended for: Maximum processing power for advanced AI processing and demanding edge computing tasks.

---

### High Reliability Performance
Platform: ROM-5620
Description: Long-term operation and harsh industrial environments.

---

## Application-Based Recommendations

### Low Power Applications
Recommended platform: ROM-2620
Typical use cases: Battery-powered devices, handheld terminals, portable HMI, edge sensors.
Performance category: Entry-Level Performance

---

### Edge AI Vision Applications
Recommended platform: AOM-5521
Typical use cases: Smart retail, vision inspection, AI cameras, video analytics.
Performance category: High Performance

---

### Industrial Gateway Applications
Recommended platform: RSB-3720
Typical use cases: Smart vending machines, industrial data gateways, factory automation systems.
Performance category: Mid-Range Performance

---

### High Reliability Industrial Applications
Recommended platform: ROM-5620
Typical use cases: Industrial control, safety-critical systems, harsh environments.
Performance category: High Reliability Performance

---

## Quick Reference

High performance platform: AOM-5521
Mid-range performance platforms: RSB-3720, ROM-5722
Low power platform: ROM-2620
Platforms based on i.MX 8M Plus (i.MX8MP): ROM-5722, RSB-3720

---

## Policy
Only platforms explicitly listed in this guide are recommended.
If a platform, scenario, or performance requirement is not listed, it is not recommended.
Otherwise answer: Not specified in the recommendation guide.

## System Behavior
If a question cannot be answered strictly based on this document, the system must NOT infer or guess.
The system must respond politely and direct users to official support:
"This information is not available in my current knowledge base. Please visit the Advantech AIM Linux Forum and leave a message. Our engineers and product managers will assist you."

---

## Response Strategy
- If a question maps directly to a defined recommendation, respond with the specific platform only.
- Do not enumerate all platforms unless the question is generic or lacks application context.
- If no explicit recommendation exists, respond with: "Not specified in the recommendation guide."
