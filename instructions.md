# Snowflake

## Documentation

- [Snowflake](https://snowflake.torproject.org/) — the Tor Project's page on what Snowflake is and who it helps.
- [Running a Snowflake proxy](https://community.torproject.org/relay/setup/snowflake/) — the Tor Project's guide for proxy operators.

## What you get on StartOS

A Snowflake proxy that starts relaying for censored Tor users the moment the service is running, and a **Dashboard** interface showing what it has done: the NAT type it detected, bandwidth relayed today, this week, this month and all-time, and an hour-by-hour chart of the last day.

There is nothing to configure and no account to make. The proxy needs no open ports, never learns what anyone is browsing, and the traffic it carries leaves the Tor network from a Tor bridge — not from your address.

## Getting set up

1. Start the service.
2. Open the **Dashboard** from the Dashboard tab.

The NAT type appears a minute or so after each start. Bandwidth and connection figures are added once an hour, so the first ones show up after the first full hour; the page refreshes itself every five minutes.

## Using Snowflake

### NAT type

**unrestricted** means clients behind strict NATs can reach your proxy, which is the most useful kind of proxy to run. **restricted** means only clients with permissive NATs can; the proxy still helps, just fewer people.

To turn a restricted proxy into an unrestricted one, forward **UDP ports 30000-30049** on your router to this server's local IP address. The proxy listens for peer connections somewhere in that range rather than one fixed port, so the whole range needs to be forwarded, not a single port. How to do this varies by router — look for "port forwarding," "port range forwarding," or "virtual servers" in its admin interface. After forwarding, restart the service and check back in a minute or so; the NAT Type tile should read **unrestricted**.

### Reading the figures

Everything on the dashboard comes from the proxy's own hourly summaries, so a figure is up to an hour behind and "0 connections" in the first hour is normal. The history lives on this server and survives restarts and updates.
