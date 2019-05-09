# Ben Capodanno
# CS251 - split_on_season.py
# This file splits all data into csv files of differing seasons
# May 9th, 2019

import data
import sys

# assumes seasons are ordered and is operating on the whole shots csv
def write_like_seasons( file ):
    with open( file ) as file:
        header = []
        buffer = []
        idx = 0
        curr_low = 1996
        curr_high = 97
        curr_season = str( curr_low ) + "-" + str( curr_high )

        for line in file:
            contents = line.split(',')
            if contents[0] == "id" or contents[0] == "numeric":
                header.append( contents )
                continue
            if contents[2] == curr_season:
                buffer.append( contents )
            else:
                print( "writing: season_" + curr_season + ".csv")
                f = open("season_" + curr_season + ".csv", "w+")
                for l in header:
                    f.write( l[1]+","+l[2]+","+l[7]+","+l[14]+","+l[15]+","+l[16]+","+l[17]+","+l[22]+"\n" )
                for l in buffer:
                    f.write( l[1]+","+l[2]+","+l[7]+","+l[14]+","+l[15]+","+l[16]+","+l[17]+","+l[22]+"\n" )
                f.close()
                curr_low += 1
                curr_high += 1
                if curr_high == 100: curr_high = 0
                if curr_high < 10: curr_season = str( curr_low ) + "-0" + str( curr_high )
                else: curr_season = str( curr_low ) + "-" + str( curr_high )
                buffer = []
            idx += 1

        print( "writing: season_" + curr_season + ".csv")
        f = open("season_" + curr_season + ".csv", "w+")
        for l in header:
            f.write( l[1]+","+l[2]+","+l[7]+","+l[14]+","+l[15]+","+l[16]+","+l[17]+","+l[22]+"\n" )
        for l in buffer:
            f.write( l[1]+","+l[2]+","+l[7]+","+l[14]+","+l[15]+","+l[16]+","+l[17]+","+l[22]+"\n" )
        f.close()
    file.close()

def main( argv ):
    if len( argv ) < 2 or len(argv) > 2:
        print( "USAGE: <" + argv[0] + "> <SHOTS CSV>")
        exit()
    write_like_seasons( argv[1] )

if __name__ == "__main__":
    main( sys.argv )
