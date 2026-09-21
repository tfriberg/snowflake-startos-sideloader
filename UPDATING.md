# Updating the upstream version

This package builds its image from the Tor Project's published `thetorproject/snowflake-proxy`
image: the `Dockerfile` copies the `proxy` binary and the GeoIP databases out of it into an
Alpine base with `busybox-extras` for the dashboard's `httpd`.

## Determining the upstream version

Upstream tags releases as `vX.Y.Z` on GitLab, and publishes the image under the same tag:

```sh
git ls-remote --tags https://gitlab.torproject.org/tpo/anti-censorship/pluggable-transports/snowflake.git 'v*' | sort -t/ -k3 -V | tail -1
curl -s 'https://hub.docker.com/v2/repositories/thetorproject/snowflake-proxy/tags?page_size=20' | jq -r '.results[].name'
```

The current pin is the `FROM thetorproject/snowflake-proxy:<tag>` line in the `Dockerfile`.

## Applying the bump

1. Change the tag in the `Dockerfile`'s first `FROM` line (keep the leading `v`).
2. Set `version` in `startos/versions/current.ts` to `X.Y.Z:0`, matching the tag without the `v`.
3. Rewrite `releaseNotes` in that file for all five locales.
4. If only the packaging changed, leave the tag alone and increment the revision instead
   (`2.14.1:0` → `2.14.1:1`).
5. Check the release notes for a change to the hourly summary line
   (`In the last 1h0m0s, there were N completed successful connections. Traffic Relayed ↓ X KB …`)
   — `dashboard/index.cgi` parses it by field position.

The Alpine base (`FROM alpine:<version>`) is bumped independently when Alpine moves.
