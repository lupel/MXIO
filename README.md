# Brief

`ping` and `curl` addresses and in case of failure notify via Slack and Email.

# Env vars
All configuration is made via environment variables.

| Name | Default | Description | Example |
| ---- | ------- | ----------- | ------- |
| DEBUG | false | Set to true for more verbosity (case insensitive) | 'tRuE' |
| CURL | ---- | List of URLs or IPs to use as targets for HTTP requests. Separated with ;;. | `https://url.com;;example.com` |
| PING | ---- | List of URLs or IPs to use as targets for ping. Separated with ;;. | `3.44.123.22;;example.com` |
| CHECK_INTERVAL | 10 | How often make requests? (in seconds) | ---- |
| FAILS_LIMIT | 3 | Quantity of fails after which host will be considered as unreachable. | ---- |
| NOTIFICATION_INTERVAL | 5 | Min interval (in minutes!) between notifications in order to avoid spamming because of failed servers. |
| NOTIFICATION_ENABLED | `true` | If `false` - all notification will be disabled (for debug) | ---- |
| EMAILS | ---- | List of emails which will be used for notification. Separated with ;;. | `a@host.com;;user@example.com` |
| SMTP_SERVER | ---- | Hostname of SMTP server | ---- |
| SMTP_PORT | 465 | SMTP port for SSL connection | ---- |
| SMTP_USER | ---- | Username which will be used for login | ---- |
| SMTP_PASSWORD | ---- | No need to describe | ---- |
| SLACK_WEBHOOK_URL | ---- | Complete webhook URL for Slack API calls | ---- |
