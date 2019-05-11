# NBA Shooting Stats Visualizer
Creative choice for Colby College CS 251 Final Project

## Usage

<b> Running the GUI </b>

download files, and run gui.py by executing
'python gui.py'


<b> Accessing Data </b>

data relevant to this visualization and in the expected format is contained in the data folder.
original shooting data can be downloaded here: https://github.com/toddwschneider/nba-shots-db
follow instructions to download, then export to csv with psql. Put into proper format by executing
'python split_on_season.py shots.csv'


<b> Player Information </b>

player population is current NBA players, despite data dating to 1996. If a data file from more
distant seasons is loaded, there will likely be very few players to analyze.


<b> Utilizing the GUI </b>

Upon opening a file, teams will populate on the right side of the window. Clicking on a team will
populate a listbox with players from that team. Click on a player, then select view shot statistics
for a detailed pop-up of shot selection and accuracy. Or, select plot in order to display a heat map
of the court with increasingly red shading based on the percentage of shots made.

## Tech

Built using Python 3 and Tkinter
