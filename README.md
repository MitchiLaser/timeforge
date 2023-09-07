# TimeForge
Create realistic looking but fake time documentation for your student job at KIT

## Call for participation

This is only a prototype with a lot of features that can be added. Unfortunately I do not have a lot of time to care for my project alone. If anyone wants to submit pull requests: Feel free to do so. 

## Installation

Installation via pip:

``` bash
$ pip install timeforge
```


## Usage

This program has currently only a command line interface. Use

``` bash
$ timeforge --help
```

to get an overview of the functionality. The PDF document with the form will be automatically downloaded from the PSE homepage.

## Configuration file

This program also supports a configuration file for the `--` command line arguments. Config file syntax is: `key = value`. Usually command line arguments are overwriting the config file. Example:

```
name = "Max Mustermann"
salary = 12.00
personell = 1234567
organisation = PSE
job = "Tutorium"
```

In this example: When calling `timeforge -c path/to/config.conf` the arguments `-n -s -p -o` and `-j` don't have to be passed anymore.

Furthermore this tool has a rudimentary but working UI. Only Linux and MAC are supported, maybe it also works on Windows. Call

``` bash
$ timeforge-tui
```

to start the user interface
