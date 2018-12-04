# Brief

Modbus slave emulator for KhAI project.
See description of protocol [there](https://bit.ly/2AHnbHK).

# Environment variables
All configuration is made via environment variables.

| Name | Default | Description | Example |
| ---- | ------- | ----------- | ------- |
| DEBUG | false | Set to true for more verbosity (case insensitive) | 'tRuE' |
| CONFIG_PATH | `/app/config.yaml` | Config for modbus-slave | `/run/secrets/config.yml` |
| SLAVES_QTY | 1 | Quantity of slaves: 1-247 | 10 |
