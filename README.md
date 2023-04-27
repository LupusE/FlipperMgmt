# Flipper Management Tools
A collection of tools to handle the Flipper Zero

Here are some of my helper for daily handling the Flipper Zero


## irfiles-import.py - Flipper-IRDB to sqlite.db

This is a tool to convert a local git repository of a [Flipper-IRDB](https://github.com/logickworkshop/Flipper-IRDB) to a SQLite3 Database.

Documentation: [https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md](https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md)

### Todo:
- ~~write a file exporter~~
  - write an android tool to generate files
  - or a webfrontend?
- write a documentation - [Ongoing](https://github.com/LupusE/FlipperMgmt/blob/main/docs/irfiles2sqlite.md)
- normalize the data
  - ~~brite a button translation table~~
  - ~~analyze the file hierachy more~~
- write a check (~~based on md5~~) to update the db
  - write an parser output to MySQL/MariaDB/MS SQL/Postgress/...
- ~~cleanup the code~~ (will never be finished)


## syncFlipper

A script to keep some github sources local up-to-date and sync with sd card (if mounted), with less write cycles.
During copy to SD there are some redirections, for better browsing at the Flipper itself.

### Installation
1. `cd ~/git && git clone https://github.com/LupusE/FlipperMgmt/`
2. `cd FlipperMgmt && sh syncFlipper`

Feel free to make the script executable with `chmod +x syncFlipper` -> `./syncFlipper`

### Usage
Just start the script from your terminal with `sh syncFlipper` or `./syncFlipper`.
The script will go through the github sources, if no local repository is found it will clone the remote one. If it is available, it will update (git pull) it.
If the SDCard is mounted at `sdcard=/media/$USER/xxx` (line 8), it will sync the files as well.
~~The main script `syncflipper` will call the subscripts. Here are the available git sources.~~
~~In `syncflipperGit` are the functions to pull the git sources and copy to SD, if availale~~
~~In `syncflipperApps` is a function to sync the apps from GuidoZ to the SD card~~

If the sd card is mounted under the given path (`sdcard=/media/$USER/xxx`,line 8), the script will sync (copy, update and delete) the local repository to the sd card.
It is hard to navigate trough too much files at the small flipper screen. Therfore I've reorganized the destination path of some repositorys for the sd card

Within the script you'll find some repositorys from **Flipper Zero Awsome**. Just comment/uncomment as you need.
A special case is the huge **UberGuidoz** repository. It contains plenty of different modules, so I've wrote a own function for this one.
The Flipper-Starnew repository splits between iButton and RFID dumps.

Before the scripting, I always wondered why some flipper directorys are 3 to 4 times bigger than the local ones. There is a difference because of the filesystem (blocksize), but not this much.
The **Flipper-IRDB** files for example are under heavy development. Sometimes a whole directory is renamed. At first I only copied the new files, the size increased. So I switched to rsync.
First advantage: The files are checked by checksum. This reduces write cycles on sd card.
Second advantage: The --delete option deletes files in the target, that are not at the source.
