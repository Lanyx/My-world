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

# UPDATE SPEED LIMITS WITH RATE OF CRUISE IN (S/KM)
    iNo_of_away = len(dSpeed_away)
    if iNo_of_away < 2:
        print("Speed limit 'away' not defined. Exiting\n\a")
        return None

    iNo_of_home = len(dSpeed_home)
    if iNo_of_home < 2:
        print("Speed limit 'home' not defined. Exiting\n\a")
        return None

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

    # ADD TRAVEL TIME TO TABLES s
    iNo_of_sj = len(dSta_jct)               # Get the number of points
    for iPtr_sj in range(0, iNo_of_sj):
        # Process each point individually, calculating its travel time from the
        # REFERENCE point
        fKm_sj = dSta_jct[iPtr_sj]["km"]    # Get the absolute distance
        iTime_away = 0                      # Allow for accumulation
        iTime_home = 0                      # The other way

    # AWAY
        iPtr_away = 0                       # To the speed table
        while iPtr_away < iNo_of_away-1:     # Go through all of them if needed.
            iPtr_away += 1
            fKm_prev = dSpeed_away[iPtr_away-1]["km"] # Milestone of limit sign
            fKm_next = dSpeed_away[iPtr_away-0]["km"] # Milestone of limit sign
            fS_per_km = dSpeed_away[iPtr_away-1]["s_per_km_crs"]

            # Speed limit not yet reached
            if fKm_sj < fKm_prev:
                break

            # We are partially in the limit
            elif fKm_prev <= fKm_sj <= fKm_next:  # We are partily in the limit
                fKm_in_lim = fKm_sj - fKm_prev  # How far since start of lim.

            # We have completed some limits already, lets add them up
            elif fKm_sj > fKm_prev:
                fKm_in_lim = fKm_next - fKm_prev

            # Time spent under the speed limit:
            fS_in_lim = round(fKm_in_lim * fS_per_km, 0)
            # ... is added to the total travel time
            iTime_away = int(iTime_away + fS_in_lim)
        dSta_jct[iPtr_sj]["away"] = iTime_away

    # HOME
        iPtr_home = 0                        # To the speed table
        while iPtr_home < iNo_of_home-1:     # Go through all of them if needed.
            iPtr_home += 1
            fKm_prev = dSpeed_home[iPtr_home-1]["km"] # Milestone of limit sign
            fKm_next = dSpeed_home[iPtr_home-0]["km"] # Milestone of limit sign
            fS_per_km = dSpeed_home[iPtr_home-1]["s_per_km_crs"]

            # We are partially in the limit
            if fKm_prev >= fKm_sj >= fKm_next:  # We are partily in the limit
                fKm_in_lim = (fKm_sj - fKm_prev)  # How far since start of lim.

            # We have completed some limits already, lets add them up
            elif fKm_sj < fKm_next:
                fKm_in_lim = fKm_next - fKm_prev

            # Speed limit not yet reached
            elif fKm_sj > fKm_next:
                break

            # Time spent under the speed limit:
            fS_in_lim = round(-fKm_in_lim * fS_per_km, 0)
            # ... is added to the total travel time
            iTime_home = int(iTime_home + fS_in_lim)

        dSta_jct[iPtr_sj]["home"] = iTime_home
        code_sj = dSta_jct[iPtr_sj]["code"]

    return dSta_jct

#-------------------------------------------------------------------------------
def calc_timetable(ccTremb):
    """ This method calculates the approximate time for the train to travel
    between the two specified points.
    """
# Open the 'lines' database.
    cLines = db.lines(ccTremb)
    cDest = db.destinations(ccTremb)
    sLine = "K00-001"

# Obtain the travel durations.
    dSta_jct = calc_pax(cLines, sLine)
    if dSta_jct == None: return None
    if len(dSta_jct) < 1: return None

# Process the array
    aKeys = dSta_jct[0].keys()
    sAll = ""
    sSep = ";"
    sAll += "km{0}type{0}code{0}name{0}s away{0}s home\n".format(sSep)

    for item in dSta_jct:
        fKm = item["km"]
        sType = item["type"]
        code = item["code"]
        sLat = " "
        if sType == "sta" and code != None:
            aNames = misc.verify_geo_code(code, cDest, bDont_warn=True)
            if aNames != None:
                sLat = aNames["lat"]

        away = item["away"]
        home = item["home"]

        sTxt = "{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}\n"
        sTxt = sTxt.format(sSep, fKm, sType, code, sLat, away, home)
        sAll += sTxt

# Write this data to a .csv file (to be used with excel)
    sFile_path = "Logs/travel_{0}.csv".format(sLine)
    eTravel = open(sFile_path, "w", encoding="utf-8")
    eTravel.write(sAll)
    eTravel.close()
    print("Please see {0}".format(sFile_path))
    return True

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
