"""
This is the simulation menu. This allows the SimPy module to 'play' on our
'lines'. I will use it to calculate a train schedule.
"""

import modules.x_database as db
import modules.x_misc as misc
import datetime as dt
import time
import math


#-------------------------------------------------------------------------------
# -: CALCULATE PASSANGER TRAIN TIMETABLE
#-------------------------------------------------------------------------------
def calc_pax(cLines, sLine):
    """ Calculates the points along the line for passanger trains. Pax trains
    assume instantanious acceleration to new speed. In practice, this takes
    several seconds."""

# Away journey
    xParam = {
        "my_id":sLine,
        "dVal.item":"sign",
        "dVal.type":"speed_away"
    }
    xRestr = {"_id":0}
    dQuery = cLines.find(xParam, xRestr)
    dQuery.sort("dVal.km")

    # Recapture the query
    dSpeed_away = []
    for query in dQuery:
        dLoc = {
            "km":query["dVal"]["km"],
            "lim":query["dVal"]["xVal"]["val"],
            "s_per_km_crs":None
        }
        dSpeed_away.append(dLoc)

# Journey home
    xParam = {
        "my_id":sLine,
        "dVal.item":"sign",
        "dVal.type":"speed_home"
    }
    xRestr = {"_id":0}
    dQuery = cLines.find(xParam, xRestr)
    dQuery.sort("dVal.km", -1)

    # Recapture the query
    dSpeed_home = []
    for query in dQuery:
        dLoc = {
            "km":query["dVal"]["km"],
            "lim":query["dVal"]["xVal"]["val"],
            "s_per_km_crs":None
        }
        dSpeed_home.append(dLoc)

# Stations.
    xParam = {
        "my_id":sLine,
        "dVal.item":"station",
        "dVal.type":"geo_code"
    }
    xRestr = {"_id":0}
    dQuery = cLines.find(xParam, xRestr)
    dQuery.sort("dVal.km")

    # Recapture the query
    dStations = []
    for query in dQuery:
        dLoc = {
            "km":query["dVal"]["km"],
            "type":"sta",
            "code":query["dVal"]["xVal"]["geo"]
        }
        dStations.append(dLoc)

# Junctions.
    xParam = {
        "my_id":sLine,
        "dVal.item":"junction",
    }
    xRestr = {"_id":0}
    dQuery = cLines.find(xParam, xRestr)
    dQuery.sort("dVal.km")

    # Recapture the query
    dJunctions = []
    for query in dQuery:
        dLoc = {
            "km":query["dVal"]["km"],
            "type":"jct",
            "code":query["dVal"]["xVal"]["line"]
        }
        dJunctions.append(dLoc)

# COMBINE STATIONS AND JUNCTIONS
    dSta_jct = sorted(dStations + dJunctions, key = lambda i:i["km"])

    print("Stations and junctions")
    for element in dSta_jct:
        print(element)

# UPDATE SPEED LIMITS WITH RATE OF CRUISE IN (S/KM)
    iNo_of_away = len(dSpeed_away)
    if iNo_of_away < 2:
        print("Speed limit 'away' not defined. Exiting\n\a")
        return None

    iNo_of_home = len(dSpeed_home)
    if iNo_of_home < 2:
        print("Speed limit 'home' not defined. Exiting\n\a")
        return None

    print("iNo_of_away: {0}; iNo_of_home: {1}".format(iNo_of_away, iNo_of_home))
    # Away
    for iPtr in range(0, iNo_of_away):
        # Table shows the speed limit from this point forward. I need to go one
        # "sign" back to see what was our range.
        iLim = dSpeed_away[iPtr]["lim"]
        # For speeds >40km/h, we travel at 5km/h below the limit.
        iCruise = misc.get_train("norm_pax", "cruise", iLim)
        # Rework the speed to allow for multiplication by distance
        if iCruise == 0:
            # Dead-end track
            dSpeed_away[iPtr]["s_per_km_crs"] = math.inf
        else:
            fS_per_km = 3600.0 / iCruise
            # Calculate the full limit duration.
            dSpeed_away[iPtr]["s_per_km_crs"] = round(fS_per_km, 1)

    # Home
    for iPtr in range(0, iNo_of_home):
        # Table shows the speed limit from this point forward. I need to go one
        # "sign" back to see what was our range.
        iLim = dSpeed_home[iPtr]["lim"]
        # For speeds >40km/h, we travel at 5km/h below the limit.
        iCruise = misc.get_train("norm_pax", "cruise", iLim)
        # Rework the speed to allow for multiplication by distance
        if iCruise == 0:
            # Dead-end track
            dSpeed_home[iPtr]["s_per_km_crs"] = math.inf
        else:
            fS_per_km = 3600.0 / iCruise
            # Calculate the full limit duration.
            dSpeed_home[iPtr]["s_per_km_crs"] = round(fS_per_km, 1)

    print("speed limits away")
    for lim in dSpeed_away:
        print(lim)

    # ADD TRAVEL TIME TO TABLES s
    print("Limits between points")
    iNo_of_sj = len(dSta_jct)
    for iPtr in range(1, iNo_of_sj):
        # How far between the entries?
        sj_km_1 = dSta_jct[iPtr-0]["km"]
        sj_km_0 = dSta_jct[iPtr-1]["km"]
        sj_km_delta = round(sj_km_1 - sj_km_0, 3)
        sj_tr_time = 0                      # Travel time. (we trying to calc)

        # SECTION START SPEED LIMIT
        iPtr_away = 1
        while iPtr_away <= iNo_of_away:
            spd_km0 = dSpeed_away[iPtr_away-1]["km"]     # Lower limit
            spd_km1 = dSpeed_away[iPtr_away-0]["km"]     # Upper limit
            if spd_km0 <= sj_km_0 <= spd_km1:            # Section start
                break                                    # Exit, we found it
            iPtr_away += 1                               # Try the next one.

        if iPtr_away == iNo_of_away:
            print("Unable to 'SECTION START' speed limit\n\a")
            return None

        # We need to adjust the pointer, since in the while loop we used the
        # upper limit as the controling factor. This is the lower limit.
        iLow = iPtr_away - 1

        # SECTION END SPEED LIMIT
        iPtr_home = 1
        while iPtr_home <= iNo_of_home:
            spd_km0 = dSpeed_away[iPtr_home-1]["km"]     # Lower limit
            spd_km1 = dSpeed_away[iPtr_home-0]["km"]     # Upper limit
            if spd_km0 <= sj_km_1 <= spd_km1:            # Section end
                break                                    # Exit, we found it
            iPtr_home += 1                               # Try the next one.

        if iPtr_home == iNo_of_home:
            print("Unable to 'SECTION END' speed limit\n\a")
            return None

        # Adjustment is needed, as the actual speed limit is the lower value.
        iHigh = iPtr_home - 1

        sTxt = ("*{4}* km:{2} ({3}) Speed limits: [{0}] -> [{1}]")
        sTxt = sTxt.format(iLow, iHigh, sj_km_1, dSta_jct[iPtr]["code"], iPtr)
        print(sTxt)

    # We are in the same speed limit.
        if iLow == iHigh:
            s_per_km = dSpeed_away[iLow]["s_per_km_crs"]
            tr_time = sj_km_delta * s_per_km
            dSta_jct[iPtr-0]["s_away"] = tr_time
        else:
            for idx in range(iLow, iHigh + 1):
                pass



#-------------------------------------------------------------------------------
def calc_timetable(ccTremb):
    """ This method calculates the approximate time for the train to travel
    between the two specified points.
    """
# Open the 'lines' database.
    cLines = db.lines(ccTremb)
    sLine = "K00-001"

    dTt = calc_pax(cLines, sLine)


#-------------------------------------------------------------------------------
# SUB-MENU
#-------------------------------------------------------------------------------
def sub_menu():
    """ Operates the simulator """
    ccTremb = db.connect()

    sSub_menu = """
SIMULATOR SUB-MENU (O):
.: Exit
X: Run Experiment (I don't know what I'm doing yet)
    """
# Go through the menu system.
    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

        # Analise the user choice
        if sInput == ".":       # Exit
            bExit = True
        elif sInput == "X":     # Open new line
            calc_timetable(ccTremb)
