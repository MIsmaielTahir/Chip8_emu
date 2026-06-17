# Chip8_emu
Simple Chip8 Emulator made in Python.

To run, download the two python files and have the ROMS folder in the same directory.

Run in Windows Command Prompt in the same directory as the two main python files with the following command:

```
python3 Chip_8_Main.py <FILE>
```
Where `<FILE>` is the game you wish to run, stored in the ROMS folder. You can find most of the original Chip8 games online, and there are some already within the ROMS folder.
See [here](https://johnearnest.github.io/chip8Archive/) for more custom ROMS.

Acknowledgements + Sources

[CowGod's Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)

[How to write an emulator (multigesture.net)](https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/)

[chiefartificier's Chip 8 Emulator](https://github.com/chiefartificer/chip8/tree/master)- Used as a general guide and refernce- mainly used for structuring OPcodes and figuring out how to draw sprites

[misa j's Chip 8 Emulator](https://github.com/misa-j/chip8-emulator) - Used as general reference and as a guide to figuring out how to have timings with threads


