# irfiles-import.py - Flipper-IRDB to sqlite.db

## HowTo init

At this time it is Linux specific. Later I will make it more portable. It is my first 100% Python project, so maybe this can take a while.

The following is just an example, you are free to use any other directory or Flipper-IRDB source.
```
$ mkdir ~/git; cd ~/git
$ git clone https://github.com/logickworkshop/Flipper-IRDB
$ git clone https://github.com/LupusE/FlipperMgmt
$ cd FlipperMgmt/
$ chmod +x irfiles_import.py
$ ./irfiles_import.py
```
Now you'll have the file `flipper_irdb.db` in `~/git/`. Just open it with your favorite SQLite tool.

I am using [Flipper-IRDB](https://github.com/logickworkshop/Flipper-IRDB) as source, right now it is the best maintained DB. But every fork will work, as long as it has not more than 3 subfolders in the hierachy and contains flipper.ir files.

## Create own .ir library files.

My first goal is to analyze and understand the fileformat better. But on the other hand, I was half way to create my own 'Universal Remote' IR library files. I wrote [https://github.com/LupusE/FlipperMgmt/blob/main/db/generate_univesalremote_file.py](https://github.com/LupusE/FlipperMgmt/blob/main/db/generate_univesalremote_file.py).

At first it should generate a `tv.ir`, but now it is able to generate almost any universal remote file. No AC at the moment.

------

## Why? Good question.

There are a lot of inconsistencies in the files, that will make it difficult to compare in plain. In a database structure you can perform much better analysis.

### Examples

If I want to create an effective 'Universal Remote', I need to know what are the most common POWER Button codes:
```
SELECT name,address,command,COUNT(name)
	FROM irbutton
	WHERE name like 'Power' AND Type like 'parsed'
	GROUP BY address,command
	ORDER BY COUNT(name) DESC
```

But there are more names for the 'Power' button. And I want only the TVs:
```
SELECT 'Power'
	   ,irbutton.protocol
	   ,irbutton.address
	   ,irbutton.command
	   ,'# ' || COUNT(irbutton.name)
	FROM irbutton
		JOIN irfile ON (irbutton.md5hash = irfile.md5hash)
	WHERE irbutton.Type LIKE 'parsed' AND irfile.category = 'TVs' AND irbutton.name IN ('POWER','Power','On_off','POWERToggle','On/Off','On_Off','power','on_off','Power_on_off','POWER_Toggle','POWER POWER','On Off','Off_on','ON/OFF','ON / OFF')
	GROUP BY irbutton.protocol,irbutton.address,irbutton.command
	ORDER BY COUNT(irbutton.name) DESC
```

Result:
|irbutton.name|irbutton.protocol|irbutton.address|irbutton.command|irbutton.count|
|---|---|---|---|---|
|Power|	Samsung32|	07 00 00 00|	02 00 00 00|	# 28|
|Power|	NEC	|04 00 00 00|	08 00 00 00|	# 27|
|Power|	SIRC	|01 00 00 00|	15 00 00 00|	# 22|
|Power|	NECext	|02 7D 00 00|	46 B9 00 00|	# 13|
|Power|	RC6	|00 00 00 00|	0C 00 00 00|	# 11|
|...|...|...|...|...|

This can be the base to create a new `assets/infrared/tv.ir` [file](https://github.com/flipperdevices/flipperzero-firmware/tree/dev/assets/resources/infrared/assets).
Be aware, that the first line for a universal remote is `Filetype: IR library file` instead of `Filetype: IR signals file`.

------

## About the SQLite database

The Database contains only two tables at the moment. The `irfiles` and the `irbuttons`. The PK (primary key) is the MD5 hash of each file, in `irfiles` and this is the FK (foregin key) in `irbuttons`.
In future use I want to check if the file already exists based on the MD5sum. Right now every run will add all entries again. If you want to refresh the DB, just delete the file and start over.

irfile
|string|category||
|string|brand||
|string|file||
|string|md5hash|PK|

irbutton
|string|name||
|string|type||
|string|protocol||
|string|address||
|string|command||
|string|md5hash|FK|

The values from irfile are taken from the Flipper-IRDB hierachy.
The values from irbutton are taken from the [flipper docs](https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/file_formats/InfraredFileFormats.md).

I've used the same table.field for `type: raw' and `type: parsed`, because it is easier to filter with `WHERE type = 'parsed'`, than work with `UNION` for example.
protocol - frequency
address - duty_cycle
command - data

## Format fields

| Name       | Use    | Type   | Description |
| --- | --- | --- | --- |
| name       | both   | string | Name of the button. Only printable ASCII characters are allowed.|
| type       | both   | string | Type of the signal. Must be `parsed` or `raw`. |
| protocol   | parsed | string | Name of the infrared protocol. Refer to `ir` console command for the complete list of supported protocols. |
| address    | parsed | hex    | Payload address. Must be 4 bytes long. |
| command    | parsed | hex    | Payload command. Must be 4 bytes long. |
| frequency  | raw    | uint32 | Carrier frequency, in Hertz, usually 38000 Hz. |
| duty_cycle | raw    | float  | Carrier duty cycle, usually 0.33. |
| data       | raw    | uint32 | Raw signal timings, in microseconds between logic level changes. Individual elements must be space-separated. Maximum timings amount is 1024. |

Source of the Table: https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/file_formats/InfraredFileFormats.md

------

Next steps:
- Analyze `type: raw`
  - write a plotter/compare the signals
- Write a UI
  - More dynamic Universal Remote .ir generation
- ... Think about more 'next steps'

