# Flipper Management Tools
A collection of tools to handle the Flipper Zero

Here I plan to release some of my helper for daily handling the FlipperZero


## irfiles-import.py - Flipper-IRDB to sqlite.db

This tool is converting a local git clone from any [Flipper-IRDB](https://github.com/logickworkshop/Flipper-IRDB) to a SQLite3 Database.

Why? Good question.

At one hand, there are a lot of inconsistencies in the files. On the other side, in a database you can perform much better analysis.
For example, If I want to create a effective 'Universal Remote', I need to know what are the most kommon POWER Button codes:
```
SELECT name,address,command, COUNT(name)
FROM irbutton
WHERE name like 'Power' AND Type like 'parsed'
GROUP BY address,command
ORDER BY COUNT(name) DESC
```

I have taken the MD5sum of the irfile as primary key. So, just for TVs:

```
SELECT name,address,command, COUNT(name)
FROM irbutton
	LEFT JOIN irfile ON irbutton.md5hash = irfile.md5hash
	
WHERE name like 'power' AND category = 'TVs' AND Type like 'parsed'
GROUP BY address,command
ORDER BY COUNT(name) DESC
```

Only 16 codes greater than 10 - In the right order to get the fastest match!
... Okay, to be fair I haven't written an experter by now. But it is fun to play.
... Connect the DB to a plotter.
... feel free to experiment, as well.

### Todo:
- Write a File Exporter
  - Write a Android Tool to generate Files
  - Or a Webfrontend?
- Write a documentation
- normalize the data
- Write a check (based on MD5) to update the db
  - Write an output to MySQL/MariaDB/MS SQL/Postgress/...
- Cleanup the code



## syncFlipper

A little script to keep the main github sources local uptodate and sync with sd card, with less write cycles.
During copy to SD there are some redirections, for better browsing at the Flipper itself.

### Installation
1. `cd ~/git && git clone https://github.com/LupusE/FlipperMgmt/`
2. `cd FlipperMgmt && sh syncFlipper`

Feel free to make the scrip executable with `chmod +x syncFlipper`

### Usage
The main script `syncflipper` will call the subscripts. Here are the available git sources.
In `syncflipperGit` are the functions to pull the git sources and copy to SD, if availale
In `syncflipperApps` is a function to sync the apps from GuidoZ to the SD card

If the sd card is mounted under the given path, the script will sync (copy, update and delete) the local repository to the sd card.
It is hard to navigate trough too much files at the small flipper screen. Therfore I've reorganized the destination path of some repositorys.

Within the script you'll find some repositorys from **Flipper ero Awsome**. Just comment/uncomment as you need.


A special case is the huge **UberGuidoz** repository. It contains plenty of different modules, so I've wrote a own function for this one.
The Flipper-Starnew repository splits between iButton and RFID dumps.

Before the scripting, I always wondered why some flipper directorys are 3 to 4 times bigger than the local ones. There is a difference because of the filesystem (blocksize), but not this much.
The **Flipper-IRDB** files for example are under much development. Sometimes a whole directory is renamed. Because I only copied the new files, the size increased. So I switched to rsync.
First advantage: The files are checked by checksum. This reduces the write cycles.
second advantage: The --delete option deletes files in the target, that ar enot at the source.

