## NBA Shooting Stats Visualizer

This project allows a user to visualize NBA shooting data through a simple GUI. The GUI makes it simple for a user to load and find players from any team. Currently, the GUI only supports players who are still in the league; loading datafiles from very old years will result in few available visualizations despite the data containing shooting data for retired players. The GUI supports both a heatmap to quickly see success rates in different court areas as well as a dialogue box that displays numeric stats to more accurately interpret the heatmap.  

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

```
Python3+
PostGreSQL 11.0+
NumPy, MatPlotLib, and TKinter
```

### Installing and Running

A step by step series of examples that tell you how to get a development env running

Follow instructions for downloading the NBA Shots Database, linked below in the 'Built With' section. This will create a local instance of a PostGreSQL database with all shot data present.

Convert this database into a CSV file with some version of below, run from psql command line

```
\COPY shots_db TO 'filename' CSV HEADER
```

Split the data into the expected per seasong shot files with

```
python split_on_season.py shots.csv
```

Run the gui

```
python gui.py
```

Within the GUI, the general workflow is to open a file, select a team from the team list box, select a player from the player list box, and view the court populate with the shooting success of that player. Once the player is selected, you are able to view the dialogue box of the numerical stats for the selected player.

## Built With

* [Python3](https://www.python.org/) - Used for all Project Scripts
* [PostGreSQL](https://www.postgresql.org/) - Database for Shot Data
* [NBA Shots DB](https://github.com/toddwschneider/nba-shots-db) - Used to Populate the pSQL Database

## Authors

* **Ben Capodanno** - *Initial work* - [bencap](https://github.com/bencap)

See also the list of [contributors](https://github.com/bencap/nba-vis/contributors) who participated in this project.
