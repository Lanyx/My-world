""" 'Road Routes' describe point-to-point transport system within the fictional
country. The end points of a combination of the following: 'importaint border',
'town', 'junction'. They work closely with junctions (probably embedded in this
file).

DEFINITIONS:
    "Junction":
        Element which changes amount of vehicles. This could be a terminus
        (border), a point where 3 or more roads meet, a town or village.
    "Road":
        Element which moves vehicles from junction to junction without change
        in vehicle count
"""

import modules.x_database as db
import modules.x_misc as misc

#
#  @   @  @@@@@  @@@@@  @      @@@@@  @@@@@  @@@@@  @@@@@   @@@@
#  @   @    @      @    @        @      @      @    @      @
#  @   @    @      @    @        @      @      @    @@@@    @@@
#  @   @    @      @    @        @      @      @    @          @
#   @@@     @    @@@@@  @@@@@  @@@@@    @    @@@@@  @@@@@  @@@@
#                                                       .

#
#   @@@@    @@@   @   @  @@@@@  @@@@@  @   @  @@@@@   @@@@
#   @   @  @   @  @   @    @      @    @@  @  @      @
#   @@@@   @   @  @   @    @      @    @ @ @  @@@@    @@@
#   @  @   @   @  @   @    @      @    @  @@  @          @
#   @   @   @@@    @@@     @    @@@@@  @   @  @@@@@  @@@@
#

#-------------------------------------------------------------------------------
# 01. Add a road
#-------------------------------------------------------------------------------
def add_road(ccTremb):
    """ Link two junctions, towns or an importaint border """
    pass

#-------------------------------------------------------------------------------
# 11. Add a junction
#-------------------------------------------------------------------------------
def add_junction(ccTremb):
    """ Add a point which adds or subtracts traffic """
    pass


#
#  @@@@   @@@@@  @      @@@@@   @@@@   @@@   @@@@@   @@@   @@@@
#   @  @  @      @      @      @      @   @    @    @   @  @   @
#   @  @  @@@@   @      @@@@   @  @@  @@@@@    @    @   @  @@@@
#   @  @  @      @      @      @   @  @   @    @    @   @  @  @
#  @@@@   @@@@@  @@@@@  @@@@@   @@@@  @   @    @     @@@   @   @
#
#-------------------------------------------------------------------------------
# SUB-MENU
#-------------------------------------------------------------------------------
def sub_menu():
    """ Provides lines """

    ccTremb = db.connect()
    cRoad = db.road_routes(ccTremb)
    sSub_menu = """
LINES SUB-MENU (R):
.: Exit
01: New Road (Todo)
11: New Junction (Todo)

    """
# Go through the menu system.
    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

        # Analise the user choice
        if sInput == ".":       # Exit
            bExit = True

        elif sInput == "01":     # Open new line
            add_road(ccTremb)

        elif sInput == "11":     # Open new line
            add_junction(ccTremb)
