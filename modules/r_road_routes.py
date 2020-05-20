""" 'Road Routes' describe point-to-point transport system within the fictional
country. They are both similar and different from rail network ('K') and
air-routes (RFU for 'Q'). Road routes also takes into account 'exit' number
which is distance based. Places do not need to be verified geo-codes.
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
LINES SUB-MENU (K):
.: Exit
1: Open New line (Record its meta-data)

    """
# Go through the menu system.
    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

        # Analise the user choice
        if sInput == ".":       # Exit
            bExit = True
        elif sInput == "1":     # Open new line
            add_line(ccTremb)
'''
        elif sInput == "3":     # Prints the line ordered by km.
            pretty_print_all(ccTremb)
        elif sInput == "4":     # Meta-data view
            pretty_print_meta(ccTremb)
        elif sInput == "5":     # New component of a line
            add_sub_comp(ccTremb)
        elif sInput == "6":
            pretty_gradient(ccTremb)
        elif sInput == "C":
            design_gradient(ccTremb)
        elif sInput == "_":
            remove_sub_comp(ccTremb)
'''
