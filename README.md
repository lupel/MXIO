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
| LISTEN_PORT | 1502 | TCP port to listen on | 502 |
| RANDOM | false | If true, then slaves start with random data | 'tRuE' |

# YAML configuration fields
Environment variables have are override any settings found in YAML.
```yaml
server:
  debug: true # bool
  port: 1502  # int
slave:
  random: true  # bool
  quantity: 22  # int
```

| Key | Default | Description | Type |
| ---- | ------- | ----------- | ------- |
| `server.debug` | false | see environment variable DEBUG | bool |
| `server.port` | 1502 | see environment variable LISTEN_PORT | int |
| `slave.random` | 1 | see environment variable RANDOM | bool |
| `slave.quantity` | 1 | see environment variable SLAVES_QTY | int |
