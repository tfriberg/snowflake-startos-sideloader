#!/bin/sh
exec snowflake-proxy -metrics -log /dev/stdout -verbose
