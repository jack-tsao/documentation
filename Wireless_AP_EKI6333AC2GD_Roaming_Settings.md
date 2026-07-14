# Wireless AP EKI6333AC-2GD Roaming Settings

These settings configure seamless roaming between multiple **EKI6333AC-2GD** access points.

> **Important**
>
> Roaming only works when the access points are connected to each other via **Ethernet (wired backhaul)**.

---

## Configuration Steps

Configure **each access point individually**.

1. Connect a computer directly to the access point using an Ethernet cable.
2. Log into the AP's web interface.
3. Apply the settings below.

---

## Configuration

| Setting | AP1 | AP2 (and additional APs) |
|---------|-----|--------------------------|
| **Operation Mode** | Access Point | Access Point |
| **2.4 GHz SSID** | `AMR-AP-2G` | `AMR-AP-2G` |
| **5 GHz SSID** | `AMR-AP-5G` | `AMR-AP-5G` |
| **Wi-Fi Channel** | Any | Different from AP1 |

### Advanced

| Setting | AP1 | AP2 |
|---------|-----|-----|
| Transmission Power | Adjust as needed | Adjust as needed |

### Security

| Setting | Value |
|---------|-------|
| Security Mode | WPA-Personal |
| WPA Version | WPA2 |
| WPA Cipher | TKIP + AES |
| Pass Phrase | Same on all APs |
| 802.11r | Enabled |
| NAS ID | Same on all APs |
| Mobility Domain | Same on all APs |

### LAN Settings

| Setting | AP1 | AP2 |
|---------|-----|-----|
| Network Mode | Static | Static |
| LAN IP | `192.168.1.2` | `192.168.1.3` |
| Subnet Mask | `255.255.255.0` | `255.255.255.0` |
| Gateway | None | None |
| DNS | None | None |
| DHCP Server | Enabled | Disabled |
| DHCP Start IP | `192.168.1.100` | N/A |

---

## Notes

- Use the **same** SSIDs, security settings, NAS ID, and Mobility Domain on every access point.
- Assign every AP a **unique static LAN IP address**.
- Configure different Wi-Fi channels on neighboring APs to minimize interference.
- Adjust transmit power to provide sufficient overlap between coverage areas for seamless roaming.

> **Warning**
>
> Do **not** set the network mode to **DHCP**.
>
> Doing so changes the AP's IP address to one assigned by the connected router.
>
> If no router is connected:
>
> - The AP will not receive an IP address.
> - The management interface will become inaccessible.
> - A factory reset will be required to regain access.

---

## Example Network

| Device | IP Address |
|---------|------------|
| AP1 | `192.168.1.2` |
| AP2 | `192.168.1.3` |
| DHCP Pool | `192.168.1.100+` |
