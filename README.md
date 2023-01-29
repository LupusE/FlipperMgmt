# Flipper Management Tools
A collection of tools to handle the Flipper Zero

Here I plan to release some of my helper for dayly handling the FlipperZero

## Installation syncFlipperGit

1. `cd ~/git && git clone https://github.com/LupusE/FlipperMgmt/`
2. `cd FlipperMgmt && sh syncFlipperGit`

Feel free to make the scrip executable with `chmod +x syncFlipperGit`

### Usage
At this moment, the script doesn't take arguments. In a futute release maybe the Mountpoint will be an option.

It uses rsync and git as external tools. And basename from coreutils.

In the source are some github repositorys from 'Flipper Zero Awsome' that can be used.
At first the skript will check if the repository exists unter $gitroot. If not, it will be cloned.

If the sd card is mounted under the given path, the script will sync (copy, update and delete) the local repository to the sd card.

It is hard to navigate trough too much files at the small flipper screen. Therfore I've reorganized the destination pathes of some repositorys.


A special case is the huge 'UberGuidoz' repository. It contains plenty of different modules, so I've wrote a own function for this one.
The Flipper-Starnew repository as well contains iButton and rfid dumps. Feel free to split.


Before the scripting, I always wondered why some flipper directorys are 3 to 4 times bigger than the local ones. There is a difference because of the filesystem (blocksize), but not this much.
The Flipper-IRDB files for example are under much development. Sometimes a whole directory is renamed. Because I only copied the new files, the size increased.

So I switched to rsync.
First advantage: The files are checked by checksum. This reduces the write cycles.
second advantage: The --delete option deletes files in the target, that ar enot at the source.

