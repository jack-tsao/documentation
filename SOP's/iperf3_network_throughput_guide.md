# iperf3 Network Throughput Test Guide

## Overview

This procedure configures the Windows PC as the **iperf3 server** and
the Ubuntu machine as the **iperf3 client** to perform a long-duration
network throughput test.

------------------------------------------------------------------------

## Requirements

-   Windows PC connected to the network
-   Ubuntu machine connected to the same network
-   IP address of the Windows PC (replace `192.168.x.x` below with the
    actual IP)

------------------------------------------------------------------------

## Windows PC (Server)

1.  Download **iperf3** using a web browser.
2.  Extract (unzip) the downloaded archive.
3.  Open Command Prompt or PowerShell.
4.  Navigate to the directory containing `iperf3.exe`.

Example:

``` powershell
cd C:\path\to\iperf3
```

5.  Start the iperf3 server:

``` powershell
.\iperf3.exe -s
```

The server will listen for incoming client connections on the default
port (5201).

------------------------------------------------------------------------

## Ubuntu Machine (Client)

1.  Install iperf3:

``` bash
sudo apt install iperf3
```

2.  Start the throughput test:

``` bash
iperf3 -c 192.168.x.x -t 86400
```

Replace `192.168.x.x` with the IP address of the Windows PC.

The `-t 86400` option runs the test for **24 hours**.

------------------------------------------------------------------------

## Notes

-   Both devices must be connected to the same network.
-   Ensure the Windows firewall allows iperf3 to accept incoming
    connections.
-   If the connection is interrupted, the test will stop and must be
    restarted.
-   Press **Ctrl+C** on either device to stop the test early.
