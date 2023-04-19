# Flipper Management Tools
A collection of tools to handle the Flipper Zero

Here I plan to release some of my helper for daily handling the FlipperZero


## irfiles-import.py - Flipper-IRDB to sqlite.db

This is a tool to convert a local git repository of a [Flipper-IRDB](https://github.com/logickworkshop/Flipper-IRDB) to a SQLite3 Database.

Documentation: [https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md](https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md)

### Todo:
- Write a File Exporter
  - Write a Android Tool to generate Files
  - Or a Webfrontend?
- Write a documentation - [Ongoing](https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md)
- normalize the data
  - ~~Write a Button translation table~~
  - analyze the file hierachy more
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

