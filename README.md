# fronius-data-grabber
Python script that grabs relevant data from fronius solar inverter and inserts it into database for logging.

```mermaid
graph LR
FI[Fronius inverter]
SC[This script]
DB[Remote database]

FI --> SC --> DB
	
```

## Dependencies

### Pyfronius Package

https://github.com/nielstron/pyfronius



## Credentials

This script reads credentials from import. Generate `credentials.py` in root directory of script.

`credentials.py`

```python
host = "hostname or ip"
user = "user"
port = "3306"
password = "password"

scheme = "scheme"
table = "table"

fronius_ip_address = "local ip of fronius inverter"
```

## Known Bugs

- Fronius device gets new IP address with each restart/power loss.

## Usage

Runs on a Raspberry Pi in the same network as the Fronius inverter. 2 Minute crontab.

```
crontab -e 

*/2 * * * * python3 /home/pi/fronius-data-grabber.py | logger
```

## Why tho?

Badass Grafana Dashboards. View them on https://zaubara.com/pv-panels/

<img src="assets/Screenshot 2023-09-02 at 21.36.09.png" alt="Screenshot 2023-09-02 at 21.36.09" />

<img src="assets/Screenshot 2023-09-02 at 21.36.15.png" alt="Screenshot 2023-09-02 at 21.36.15" />

<img src="assets/Screenshot 2023-09-02 at 21.37.32.png" alt="Screenshot 2023-09-02 at 21.37.32" />
