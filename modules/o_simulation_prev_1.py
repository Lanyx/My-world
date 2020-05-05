"""
This is the simulation menu. This allows the SimPy module to 'play' on our
'lines'. I will use it to calculate a train schedule.
"""

import modules.x_database as db
import modules.x_misc as misc
import simpy
import math

#-------------------------------------------------------------------------------
# -. Run database trains
#-------------------------------------------------------------------------------
def read_track_events(ccTremb):
    """ Extracts the track events from the DB, ordered by km, with some
    redundant data removed."""
    # /!\ NOTE: HARDCODED TO THE K00-001 LINE
    # TODO: ADD FLEXIBILITY
    cLine = db.lines(ccTremb)           # Get the database
    xParam = {
        "my_id":"K00-001",              # Line identifier (VAA - FS0)
        "tag":"val",                    # Not the header
        "dVal.item":"track"             # Only track changes worry us.
        }
    xRestr = {"_id":0, "tag":0, "dVal.item":0}
    dQuery = cLine.find(xParam, xRestr) # The search itself
    dQuery.sort("dVal.km")              # Arrange by km.

    # Extract data
    dData = []
    for query in dQuery:
        dData.append(query)

    # Debug: to see what the track data actually looks like.
    if False:
        sFile_path = "Logs/scratch.txt"
        eScratch = open(sFile_path, "w", encoding="utf-8")
        sAll = ""
        for item in dData:
            sAll += "{0}\n".format(item)
        eScratch.write(sAll)
        eScratch.close()
    return dData                    # Return the array of tracks.

#-------------------------------------------------------------------------------
def build_sections(adTracks):
    """
    Method extracts track distance and their count between the switches.
    Effectively, method builds the dimensions of the resource.
    """
    aSection = []                   # For access via a numeric index.
    iEvent_cnt = len(adTracks)
    for iCnt in range(1, iEvent_cnt):
        dNow = adTracks[iCnt]               # Current sample
        dPrv = adTracks[iCnt-1]             # Previous

        # We need to be on the same line.
        if dNow["my_id"] != dPrv["my_id"]:
            continue

        # calculate the change in distance
        fD_km = dNow["dVal"]["km"] - dPrv["dVal"]["km"]
        if fD_km < 0:
            print("\n\aERROR: LIST NOT SORTED")
            return None
        if fD_km == 0:
            print("\n\aERROR: DUPLICATED MILESTONE")
            return None
        fD_km = round(fD_km, 2)

        # Verify that the tracks are consistent.
        iTrack_prv = 0
        iTrack_now = 0
        prv_type = dPrv["dVal"]["type"]
        if prv_type == "start_all":
            iTrack_prv = dPrv["dVal"]["xVal"]       # Straight integer
        elif prv_type == "merge" or prv_type == "diverge":
            iTrack_prv = dPrv["dVal"]["xVal"]["iAft"]
        else:
            # TODO: How do I deal with junctions?
            print("\n\aERROR: UNKNOWN TRACK TYPE")
            return None

        # Extract the second parameter
        now_type = dNow["dVal"]["type"]
        if now_type == "start_all":
            iTrack_now = dNow["dVal"]["xVal"]       # Straight integer
        elif now_type == "merge" or now_type == "diverge":
            iTrack_now = dNow["dVal"]["xVal"]["iBef"]
        else:
            # TODO: How do I deal with junctions?
            print("\n\aERROR: UNKNOWN TRACK TYPE")
            return None

        # Check for consistency
        if iTrack_now != iTrack_prv:
            print("\n\aWARNING: TRACK COUNT NOT CONSISTENT\n")

        # Build up the element with a few RFU's
        dElement = {
            "sNme": "Trk_{0}".format(iCnt), # Name (like "VAA-0==>VAA-1")
            "fLen": fD_km,                  # Length of the section
            "iTrk": iTrack_prv,             # track count
            "fSpd": 60,                     # Average track speed limit (TODO)
            "oRes": None,                   # The resource object
            }
        aSection.append(dElement)

    # Debug: to see what the track data actually looks like.
    if False:
        sFile_path = "Logs/scratch.txt"
        eScratch = open(sFile_path, "w", encoding="utf-8")
        sAll = ""
        for item in aSection:
            sAll += "{0}\n".format(item)
        eScratch.write(sAll)
        eScratch.close()

    return aSection
#-------------------------------------------------------------------------------
def operate_train(oEnv, adSections, iStart, iEnd, sName, eAtc):
    """
    Method describes the motion of the trains.
    """
# Prepare an external trip log
    sFile_path = "Logs/o_{0}_trip.txt".format(sName)
    eTrip = open(sFile_path, "w", encoding="utf-8")
    sAll = ""

# Cycle through the route
    xPrev_req = None                        # Release track after delay
    for iSel in range(iStart, iEnd):
        dSec = adSections[iSel]             # Select the stage

    # Request the section.
        xReq = dSec["oRes"].request()       # Request entry onto the section
        # Status report formatting
        sTxt = "[{0:02d}:{1:02d}] {2} requests {3}"
        iH, iM = divmod(oEnv.now, 60)
        sTxt = sTxt.format(iH, iM, sName, dSec["sNme"])

        print(sTxt)                         # To screen
        eAtc.write("{0}\n".format(sTxt))    # For "air traffic control"
        sAll += "{0}\n".format(sTxt)
        yield xReq                          # Ask for permission

    # Permission was granted, we now enter the track
        sTxt = "[{0:02d}:{1:02d}] {2} cleared to {3}"
        iH, iM = divmod(oEnv.now, 60)
        sTxt = sTxt.format(iH, iM, sName, dSec["sNme"])

        print(sTxt)
        eAtc.write("{0}\n".format(sTxt))
        sAll += "{0}\n".format(sTxt)

    # End of train needs time to leave the previous section
        yield oEnv.timeout(1)
        if iSel > iStart:       # This doesn't work on first iteration
            adSections[iSel-1]["oRes"].release(xPrev_req)
            xPrev_req = xReq    # Prepare this request to be released.

            sTxt = "[{0:02d}:{1:02d}] {2} vacated {3}"
            iH, iM = divmod(oEnv.now, 60)
            sTxt = sTxt.format(iH, iM, sName, adSections[iSel-1]["sNme"])

            print(sTxt)
            eAtc.write("{0}\n".format(sTxt))
            sAll += "{0}\n".format(sTxt)

    # Spend time traveling in this section
        # spd = dist / time ; time = dist / spd
        fTime = dSec["fLen"] / dSec["fSpd"]     # km / km/h = hours
        fTime = fTime * 60.0        # minutes
        iTime = math.ceil(fTime)    # Round up.
        iTime -= 1                  # We already waited one unit
        if iTime > 0:
            yield oEnv.timeout(iTime)

    # Loop completed.
    sTxt = "[{0:02d}:{1:02d}] {2} Trip completed"
    iH, iM = divmod(oEnv.now, 60)
    sTxt = sTxt.format(iH, iM, sName)
    eAtc.write("{0}\n".format(sTxt))
    print(sTxt)
    sAll += "{0}\n".format(sTxt)

    eTrip.write(sAll)
    eTrip.close()

#-------------------------------------------------------------------------------
def operate_system(oEnv, adSections, eAtc):
    """
    Method sets up two trains, and describes their motion.
    """
    # Generate the timetable in the opposite direction
    adReversed = list(reversed(adSections))

    # VA -> FS train
    oEnv.process(operate_train(oEnv, adSections, 0, 15, "VA-FS", eAtc))
    yield oEnv.timeout(5)

    # FS -> VA train
    oEnv.process(operate_train(oEnv, adReversed, 0, 15, "FS-VA", eAtc))
    yield oEnv.timeout(0)



################################################################################
def run_trains(ccTremb):
    """
    This is an attempt to import the route from the database and run a train
    over it.
    """
    # Get the changes in track configurations.
    adTracks = read_track_events(ccTremb)
    # Sections are stretches of track between events.
    # These will become 'resources'
    adSections = build_sections(adTracks)
    if adSections == None:
        return None

    # START UP THE ENVIRONMENT
    oEnv = simpy.Environment()
    # Build the resources
    for dSection in adSections:
        iTracks = dSection["iTrk"]           # Number of tracks for the resource
        dSection["oRes"] = simpy.Resource(oEnv, iTracks)

    # Prepare the ATC (Air Traffic Control log)
    sFile_path = "Logs/o_ATC_trip.txt"
    eAtc = open(sFile_path, "w", encoding="utf-8")

# RUN!!
    oEnv.process(operate_system(oEnv, adSections, eAtc))
    oEnv.run(until=60*24)

    eAtc.close()

#-------------------------------------------------------------------------------
# -. Run lights
#-------------------------------------------------------------------------------
def qTrains_azufi(oEnv):
    oR_sta_1 = simpy.Resource(oEnv, 4)      # Station 1 has 4 tracks
    oR_track_1 = simpy.Resource(oEnv, 1)    # Track 1 can hold 1 train
    oR_track_2 = simpy.Resource(oEnv, 1)    # Track 2 can hold 1 train
    oR_sta_2 = simpy.Resource(oEnv, 2)      # Station 2 can hold 2 trains

    req_s1 = oR_sta_1.request()             # Wait to be allowed to "spawn"
    yield req_s1
    print("[{0:>5}] VIR: Good Morning.".format(oEnv.now))
    yield oEnv.timeout(2)                    # Load pax
# STATION_1 --> TRACK_1
    print("[{0:>5}] VIR: Request T1.".format(oEnv.now))
    req_t1 = oR_track_1.request()     # Wait to enter track 2
    yield req_t1
    print("[{0:>5}] VIR: Cleared to T1.".format(oEnv.now))
    yield oEnv.timeout(1)                    # Transiton from station to track
    oR_sta_1.release(req_s1)                 # Transitoined off the station
    print("[{0:>5}] VIR: S1 vacant.".format(oEnv.now))
# TRACK 1
    yield oEnv.timeout(10)                   # Travel time
# TRACK_1 --> TRACK_2
    print("[{0:>5}] VIR: Request T2.".format(oEnv.now))
    req_t2 = oR_track_2.request()
    yield req_t2
    print("[{0:>5}] VIR: Cleared to T2.".format(oEnv.now))
    yield oEnv.timeout(1)                    # Transition time
    oR_track_1.release(req_t1)
    print("[{0:>5}] VIR: T1 vacant.".format(oEnv.now))
# TRACK_2
    yield oEnv.timeout(15)                   # Travel time
# TRACK_2 --> STATION_2
    print("[{0:>5}] VIR: Request S2.".format(oEnv.now))
    req_s2 = oR_sta_2.request()
    yield req_s2
    print("[{0:>5}] VIR: Cleared to S2.".format(oEnv.now))
    yield oEnv.timeout(1)                    # Transition time
    oR_track_2.release(req_t2)
    print("[{0:>5}] VIR: T2 vacant.".format(oEnv.now))

    print("\n[{0:>5}] VIR: At platform S2\n".format(oEnv.now))
# STATION_2 --> TRACK_2
    yield oEnv.timeout(30)
    print("[{0:>5}] VIR: Request T2".format(oEnv.now))
    req_t2_b = oR_track_2.request()
    yield req_t2_b
    print("[{0:>5}] VIR: Cleared to T2".format(oEnv.now))
    yield oEnv.timeout(1)
    oR_sta_2.release(req_s2)
    print("[{0:>5}] VIR: S2 Vacant".format(oEnv.now))


def run_trains_azufi(ccTremb):

    oEnv = simpy.Environment()          # Open the framework
    oEnv.process(qTrains_azufi(oEnv))
    oEnv.run(until=900)

#-------------------------------------------------------------------------------
# -. Run lights
#-------------------------------------------------------------------------------
def qLights(oEnv):
    while True:
        print("GRN at {0}".format(oEnv.now))
        yield oEnv.timeout(20)
        print("YEL at {0}".format(oEnv.now))
        yield oEnv.timeout(4.5)
        print("RED at {0}".format(oEnv.now))
        yield oEnv.timeout(30)

def run_lights(ccTremb):
    oEnv = simpy.Environment()              # Open the simulation background
    oEnv.process(qLights(oEnv))
    oEnv.run(until=600)
    print("--- at {0}".format(oEnv.now))

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
            run_trains(ccTremb)
