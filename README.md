This was a tool I created as a stopgap before migrating to Kubernetes. One of the biggest pain points in having to create subdirectory domains ahead of adding a new service that doesnt' properly support path proxies.

The auto_dns.sh and create_dns.py was designed to be run as part of starting and stopping caddy service. Downside is, because of the way ExecReload works (it doesn't support running ExecStartPre scripts), the reload command is not good for adding more proxies. The best suggestion is to replace the caddy file with the one in this repo.

There are a few requirements to get started:

Python3 is installed
Python3 Venv is also installed.
You change the path to the auto_dns.sh script in caddy.service to wherever the script, python script and requirements.txt lives.
You are using DigitalOcean DNS and have a token
