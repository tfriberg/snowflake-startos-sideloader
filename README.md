<p align="center">
  <img src="icon.svg" alt="Snowflake Logo" width="21%">
</p>

# Snowflake on StartOS

> Everything not listed in this document should behave the same as upstream
> Snowflake. If a feature, setting, or behavior is not mentioned here, the
> upstream documentation is accurate and fully applicable — see the
> Documentation section of `instructions.md` for links.

[Snowflake](https://snowflake.torproject.org/) is a Tor pluggable transport that gets people in censored networks onto Tor by relaying their traffic through volunteer-run proxies. This package runs the standalone Go proxy from the Tor Project's own image, with every setting left at upstream's defaults, and adds a small web dashboard that turns the proxy's hourly log summaries into NAT type, bandwidth and connection figures.

- **Upstream repo:** <https://gitlab.torproject.org/tpo/anti-censorship/pluggable-transports/snowflake>
- **Wrapper repo:** <https://github.com/Start9-Community/snowflake-startos-sideloader>

---

## Table of Contents

- [Image and Container Runtime](#image-and-container-runtime)
- [Volume and Data Layout](#volume-and-data-layout)
- [File Models](#file-models)
- [Dependencies](#dependencies)
- [Network Access and Interfaces](#network-access-and-interfaces)
- [Installation and First-Run Flow](#installation-and-first-run-flow)
- [Actions](#actions)
- [Tasks](#tasks)
- [Health Checks](#health-checks)
- [Backups and Restore](#backups-and-restore)
- [Limitations and Differences](#limitations-and-differences)
- [Quick Reference for AI Consumers](#quick-reference-for-ai-consumers)

---

## Image and Container Runtime

One image, built by this repo's `Dockerfile`: the statically linked `proxy` binary and the GeoIP databases are copied out of the Tor Project's published `thetorproject/snowflake-proxy` image into an Alpine base that also carries `busybox-extras` for its `httpd`. Upstream's image is `FROM scratch`, with no shell, which is the only reason the package does not run it as-is.

| Property      | Value                                                 |
| ------------- | ----------------------------------------------------- |
| Image         | `snowflake`, built from `./Dockerfile`                |
| Base          | `alpine`, with `thetorproject/snowflake-proxy`'s binary |
| Architectures | x86_64, aarch64                                       |
| User          | root                                                  |

Two daemons share one subcontainer:

| Subcontainer | Daemon      | Command                                                              | Purpose                                              |
| ------------ | ----------- | -------------------------------------------------------------------- | ---------------------------------------------------- |
| `snowflake`  | `proxy`     | `snowflake-proxy -log /data/snowflake.log -metrics -metrics-address 127.0.0.1` | The proxy itself                             |
| `snowflake`  | `dashboard` | `busybox-extras httpd -f -p 80 -h /www`                              | Serves the stats page, rendered per request by a CGI |

The proxy runs with upstream's defaults — broker, STUN servers, relay pattern, unlimited capacity, hourly summaries — plus two flags. `-log` makes it append its event log (start, NAT type, hourly summary) to a file on the data volume as well as to stderr, which is what the dashboard reads; `-metrics` binds a Prometheus endpoint on loopback port 9999, which is what the health check probes, since the proxy opens no other port. Nothing reads the metrics beyond that.

The dashboard is `dashboard/index.cgi`, installed as `/www/cgi-bin/index.cgi`. `httpd` runs it for every request to `/`: one `awk` pass over the log produces the page, so it is always current and there is no generator loop. The page refreshes itself every five minutes.

## Volume and Data Layout

One volume, holding the proxy's log.

| Volume | Mount Point | Purpose                                                  |
| ------ | ----------- | -------------------------------------------------------- |
| `main` | `/data`     | `snowflake.log`, the event log the dashboard is built from |

The log is append-only and grows by a few lines an hour: it holds no client addresses (upstream's logging scrubs them unless `-unsafe-logging` is passed, which the package never does). Nothing else is stored.

## File Models

None. The proxy takes no configuration file, and the package passes no options the user can change.

## Dependencies

None.

## Network Access and Interfaces

One interface, serving the dashboard. The proxy listens on UDP ports 30000-30049 (`-ephemeral-ports-range 30000:31000`) for WebRTC/ICE peer connections; forwarding that range on the router is what turns a restricted proxy into an unrestricted one (see instructions.md).

| Interface | Id   | Type | Port | Description                                             |
| --------- | ---- | ---- | ---- | ------------------------------------------------------- |
| Dashboard | `ui` | ui   | 80   | NAT type, bandwidth and connections relayed by this proxy |

The port is bound on the `ui-multi` MultiHost over plain HTTP and is not masked. The page is read-only and holds nothing sensitive, but it does reveal that this server runs a Snowflake proxy and how much it relays.

The proxy makes outbound connections only: HTTPS to the Snowflake broker to be matched with clients, STUN to learn its public address and NAT type, WebRTC (UDP, on ephemeral ports) to the clients themselves, and WebSocket to the Snowflake bridge it relays them to. It listens for nothing, so no port forwarding is needed — though a NAT that lets UDP in freely ("unrestricted" on the dashboard) can serve clients whose own NAT is restrictive, and is worth having if the router allows it.

## Installation and First-Run Flow

Nothing to configure. Install, start, and the proxy registers with the broker on its own; the dashboard's NAT type appears within a minute or two, and the first bandwidth figures after the first full hour. No task, no account, no credential.

## Actions

None.

## Tasks

None. This package raises no tasks, so the service is never held on a prompt and its ordinary controls are always available.

## Health Checks

One check per daemon.

| Check       | Displayed         | Method                                   |
| ----------- | ----------------- | ---------------------------------------- |
| `proxy`     | "Snowflake Proxy" | Loopback port 9999 (metrics) is listening |
| `dashboard` | "Dashboard"       | Port 80 is listening                     |

**Snowflake Proxy** failing means the proxy process is not running — the metrics listener is bound at startup, before any network activity, so a failure is a crash, not a connectivity problem, and the service logs carry the reason. The check says nothing about whether the proxy is reaching the broker or serving anyone; the dashboard's NAT type staying at "unknown" and the hourly summaries showing zero connections are the signals for that, and both usually mean outbound UDP or the broker is blocked.

**Dashboard** failing means `httpd` did not start, which on a working image does not happen.

## Backups and Restore

The `main` volume is copied wholesale — `sdk.Backups.ofVolumes('main')` — so a backup is the event log, and a restored instance starts with its dashboard history intact. The proxy has no identity and nothing to re-establish: it registers with the broker afresh on every start.

## Limitations and Differences

1. **Mostly no configuration.** Capacity, broker, STUN servers, relay pattern and the summary interval all stay at upstream's defaults; there is no action to change them. The one exception is `-ephemeral-ports-range`, narrowed from the OS's wide default to a fixed 50-port UDP range (30000-30049) so operators have something forwardable on their router for NAT traversal.
2. **Statistics come from the log, not from the proxy.** The dashboard adds up the hourly summaries the proxy writes, so it lags real time by up to an hour, shows nothing for the first hour, and starts from zero on a fresh install.
3. **The dashboard's history is only as old as the log.** Deleting `snowflake.log` resets it.

---

## Quick Reference for AI Consumers

```yaml
package_id: snowflake
image: snowflake # built from ./Dockerfile on thetorproject/snowflake-proxy
architectures:
  - x86_64
  - aarch64
subcontainers:
  - snowflake # proxy + dashboard httpd
volumes:
  main: /data # snowflake.log
file_models: []
startos_managed_env_vars: []
dependencies: []
interfaces:
  ui: { type: ui, port: 80 }
actions: []
tasks: []
health_checks:
  - proxy # displayed "Snowflake Proxy"
  - dashboard # displayed "Dashboard"
```
