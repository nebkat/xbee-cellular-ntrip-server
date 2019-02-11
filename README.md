# Digi XBee® Cellular Micropython NTRIP Server
Micropython script for uploading correction data (or any UART data) to an NTRIP caster.

[Digi Micropython Programming Guide](https://www.digi.com/resources/documentation/digidocs/pdfs/90002219.pdf)

### Configuration
Modify values in config.json and upload to root folder of device.

```
{
	"name": Server identification to caster
	"mountpoint": Mountpoint to push data to
	"caster": {
		"host": Caster hostname or IP
		"port": Caster port
		"username": Caster username (not required for NTRIP v1)
		"password": Caster password
		"version": NTRIP version (1 or 2)
	},
}
```
