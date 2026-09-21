#!/bin/sh
# Renders the stats page from the proxy's log: its hourly "In the last 1h0m0s,
# there were N completed successful connections. Traffic Relayed ↓ X KB (…),
# ↑ Y KB (…)." summaries, the NAT type it detects, and its start line.
LOG_FILE="${LOG_FILE:-/data/snowflake.log}"

printf 'Content-Type: text/html; charset=utf-8\r\n\r\n'

awk -v now="$(date -u +%s)" -v generated="$(date -u +%Y-%m-%dT%H:%M:%SZ)" -v logfile="$LOG_FILE" '
function epoch(d, t,   D, T, y, m, dd, era, yoe, doy, doe) {
  split(d, D, "/"); split(t, T, ":")
  y = D[1] + 0; m = D[2] + 0; dd = D[3] + 0
  if (m <= 2) y--
  era = int((y >= 0 ? y : y - 399) / 400)
  yoe = y - era * 400
  doy = int((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + dd - 1
  doe = yoe * 365 + int(yoe / 4) - int(yoe / 100) + doy
  return (era * 146097 + doe - 719468) * 86400 + T[1] * 3600 + T[2] * 60 + T[3]
}
# The proxy reports decimal kilobytes (bytes / 1000).
function fmt(kb) { return kb >= 1000000 ? sprintf("%.2f GB", kb / 1000000) : sprintf("%.1f MB", kb / 1000) }
function trend(cur, prev, since,   pct) {
  if (prev <= 0 || first_ep > since) return ""
  pct = (cur - prev) / prev * 100
  if (pct < 0) return sprintf(" <span class=\"trend trend-down\">&#9660; %d%%</span>", -pct + 0.5)
  return sprintf(" <span class=\"trend trend-up\">&#9650; %d%%</span>", pct + 0.5)
}
function esc(s) { gsub(/&/, "\\&amp;", s); gsub(/</, "\\&lt;", s); gsub(/>/, "\\&gt;", s); return s }
BEGIN {
  today_start = now - (now % 86400)
  week_start = now - 7 * 86400
  month_start = now - 30 * 86400
  yesterday_end = today_start - 86400 + (now - today_start)
  n = 0; nat = "unknown"
}
/NAT type:/ { nat = $0; sub(/.*NAT type: */, "", nat); nat_ts = $1 " " $2 }
/Proxy starting/ { start_ts = $1 " " $2 }
# Each summary is logged through two loggers, so drop exact repeats.
/completed successful connections/ && !seen[$0]++ {
  ep = epoch($1, $2); conn = $9 + 0; kb = $16 + $21
  if (!first_ep) first_ep = ep
  n++; ts[n] = $1 " " $2; tm[n] = $2; c[n] = conn; dn[n] = $16 + 0; up[n] = $21 + 0
  total_conn += conn; total_kb += kb
  if (ep >= month_start) { month_conn += conn; month_kb += kb }
  else if (ep >= month_start - 30 * 86400) prev_month_kb += kb
  if (ep >= week_start) { week_conn += conn; week_kb += kb }
  else if (ep >= week_start - 7 * 86400) prev_week_kb += kb
  if (ep >= today_start) { today_conn += conn; today_kb += kb }
  else if (ep >= today_start - 86400 && ep < yesterday_end) prev_today_kb += kb
}
END {
  first = n > 24 ? n - 23 : 1
  shown = n - first + 1
  for (i = first; i <= n; i++) if (dn[i] + up[i] > max_kb) max_kb = dn[i] + up[i]
  nat_class = tolower(nat) == "unrestricted" ? "nat-good" : tolower(nat) == "restricted" ? "nat-warn" : ""

  print "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
  print "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
  print "<meta http-equiv=\"refresh\" content=\"300;url=/?t=" now "\">"
  print "<link rel=\"icon\" href=\"/favicon.svg\">"
  print "<title>Snowflake Proxy Stats</title><style>"
  print ":root{color-scheme:light dark;--bg:#f9f9f7;--card:#ffffff;--text:#0b0b0b;--muted:#6b6a66;--border:rgba(0,0,0,.1);--good:#1a7f37;--warn:#9a6700;}"
  print "@media (prefers-color-scheme:dark){:root{--bg:#0d0d0d;--card:#1a1a19;--text:#fff;--muted:#c3c2b7;--border:rgba(255,255,255,.12);}}"
  print "*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,\"Segoe UI\",sans-serif}"
  print ".container{max-width:960px;margin:0 auto;padding:28px 18px 50px}"
  print "h1{font-size:20px;margin:0 0 4px;display:flex;align-items:center;gap:8px}.meta{color:var(--muted);font-size:12px;margin-bottom:20px}"
  print ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:28px}"
  print ".tile{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px}"
  print ".label{font-size:12px;color:var(--muted);margin-bottom:6px}.value{font-size:22px;font-weight:600}"
  print ".sub{font-size:11px;color:var(--muted);margin-top:4px}"
  print ".nat-good{color:var(--good)}.nat-warn{color:var(--warn)}"
  print ".trend{font-size:12px;font-weight:600}.trend-up{color:var(--good)}.trend-down{color:var(--warn)}"
  print "table{width:100%;border-collapse:collapse;font-size:12px}"
  print "th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--border)}"
  print "th{color:var(--muted);font-weight:600}"
  print "h2{font-size:14px;margin:24px 0 8px}.peak{color:var(--muted);font-weight:400;font-size:12px}"
  print ".bar-chart{display:flex;align-items:flex-end;gap:3px;height:100px;padding:8px;background:var(--card);border:1px solid var(--border);border-radius:10px}"
  print ".bar{flex:1 1 auto;min-width:4px;background:var(--good);border-radius:2px 2px 0 0;transition:background .15s}"
  print ".bar:hover{background:#2ea043}"
  print "footer{margin-top:20px;color:var(--muted);font-size:11px}"
  print "</style></head><body><div class=\"container\">"
  print "<h1><svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.5\" stroke-linecap=\"round\" aria-hidden=\"true\"><line x1=\"20.23\" y1=\"16.75\" x2=\"3.77\" y2=\"7.25\"/><line x1=\"12\" y1=\"21.5\" x2=\"12\" y2=\"2.5\"/><line x1=\"3.77\" y1=\"16.75\" x2=\"20.23\" y2=\"7.25\"/><line x1=\"17.2\" y1=\"15\" x2=\"20.57\" y2=\"11.25\"/><line x1=\"17.2\" y1=\"15\" x2=\"15.63\" y2=\"19.79\"/><line x1=\"12\" y1=\"18\" x2=\"16.93\" y2=\"19.04\"/><line x1=\"12\" y1=\"18\" x2=\"7.07\" y2=\"19.04\"/><line x1=\"6.8\" y1=\"15\" x2=\"8.37\" y2=\"19.79\"/><line x1=\"6.8\" y1=\"15\" x2=\"3.43\" y2=\"11.25\"/><line x1=\"6.8\" y1=\"9\" x2=\"3.43\" y2=\"12.75\"/><line x1=\"6.8\" y1=\"9\" x2=\"8.37\" y2=\"4.21\"/><line x1=\"12\" y1=\"6\" x2=\"7.07\" y2=\"4.96\"/><line x1=\"12\" y1=\"6\" x2=\"16.93\" y2=\"4.96\"/><line x1=\"17.2\" y1=\"9\" x2=\"15.63\" y2=\"4.21\"/><line x1=\"17.2\" y1=\"9\" x2=\"20.57\" y2=\"12.75\"/></svg>Snowflake Proxy Stats</h1>"
  print "<div class=\"meta\">Generated " generated " &middot; Snowflake Dashboard powered by ruxal</div>"

  print "<div class=\"grid\">"
  printf "<div class=\"tile\"><div class=\"label\">NAT Type</div><div class=\"value %s\">%s</div>%s</div>", nat_class, esc(nat), nat_ts ? "<div class=\"sub\">as of " esc(nat_ts) " UTC</div>" : ""
  printf "<div class=\"tile\"><div class=\"label\">Bandwidth (today)</div><div class=\"value\">%s%s</div><div class=\"sub\">%d connections</div></div>", fmt(today_kb), trend(today_kb, prev_today_kb, today_start - 86400), today_conn
  printf "<div class=\"tile\"><div class=\"label\">Bandwidth (7 days)</div><div class=\"value\">%s%s</div><div class=\"sub\">%d connections</div></div>", fmt(week_kb), trend(week_kb, prev_week_kb, week_start - 7 * 86400), week_conn
  printf "<div class=\"tile\"><div class=\"label\">Bandwidth (30 days)</div><div class=\"value\">%s%s</div><div class=\"sub\">%d connections</div></div>", fmt(month_kb), trend(month_kb, prev_month_kb, month_start - 30 * 86400), month_conn
  printf "<div class=\"tile\"><div class=\"label\">Bandwidth (all-time)</div><div class=\"value\">%s</div><div class=\"sub\">%d connections</div></div>", fmt(total_kb), total_conn
  printf "<div class=\"tile\"><div class=\"label\">Connections (latest hour)</div><div class=\"value\">%s</div></div>", n ? c[n] : "-"
  printf "<div class=\"tile\"><div class=\"label\">Hourly summaries logged</div><div class=\"value\">%d</div></div>", n
  if (start_ts) printf "<div class=\"tile\"><div class=\"label\">Proxy last started</div><div class=\"value\" style=\"font-size:15px\">%s</div><div class=\"sub\">UTC</div></div>", esc(start_ts)
  print "</div>"

  if (n) {
    printf "<h2>Bandwidth, last %d hours <span class=\"peak\">(peak: %s)</span></h2><div class=\"bar-chart\">", shown, fmt(max_kb)
    for (i = first; i <= n; i++) {
      kb = dn[i] + up[i]
      pct = max_kb > 0 ? int(kb * 100 / max_kb) : 0
      if (pct < 3) pct = 3
      printf "<div class=\"bar\" style=\"height:%d%%\" title=\"%s UTC: %s\"></div>", pct, esc(tm[i]), fmt(kb)
    }
    print "</div>"
    print "<h2>Recent hourly activity</h2><table><thead><tr><th>Hour ending (UTC)</th><th>Connections</th><th>Down</th><th>Up</th></tr></thead><tbody>"
    for (i = first; i <= n; i++) printf "<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>", esc(ts[i]), c[i], fmt(dn[i]), fmt(up[i])
    print "</tbody></table>"
  } else {
    print "<h2>Bandwidth, last 0 hours</h2><p class=\"sub\">No hourly summaries logged yet.</p>"
    print "<h2>Recent hourly activity</h2><p class=\"sub\">No hourly summaries logged yet.</p>"
  }
  printf "<footer>%d hourly summaries parsed from %s.</footer></div></body></html>\n", n, esc(logfile)
}' "$( [ -f "$LOG_FILE" ] && printf %s "$LOG_FILE" || printf /dev/null )"
