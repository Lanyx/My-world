""" 'Lines' describe point-to-point transport lines. At first, they are modeled
on the railway system. The option will exist to extend them to road routes,
shipping lanes, air routes.
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

#-------------------------------------------------------------------------------
def qVerify_line(sK_code, ccTremb):
    """
    Method checks the database for the existance of the K-code header. It then
    returns the route name details.
    """
# Access database
    cLine = db.lines(ccTremb)

# Verify that the database exists:
    cLine = db.lines(ccTremb)
    xParam = {"my_id":sK_code, "tag":"meta"}
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)

    # Extract the data
    dMeta = ""
    for query in dQuery:
        dMeta = query       # Save data for further processing

    if dMeta == "":
        print("\n\aLine {0} couldn't be found".format(sK_code))
        return None

    sTxt = "Route [{0}], Named '{1}'"
    sTxt = sTxt.format(dMeta["dVal"]["route_no"], dMeta["dVal"]["sRoute_name"])
    return sTxt


#
#   @@@@    @@@   @   @  @@@@@  @@@@@  @   @  @@@@@   @@@@
#   @   @  @   @  @   @    @      @    @@  @  @      @
#   @@@@   @   @  @   @    @      @    @ @ @  @@@@    @@@
#   @  @   @   @  @   @    @      @    @  @@  @          @
#   @   @   @@@    @@@     @    @@@@@  @   @  @@@@@  @@@@
#


#-------------------------------------------------------------------------------
# 1. Add to the lines
#-------------------------------------------------------------------------------
def add_line(ccTremb):
    """ Creates a new railway line meta-data header in the database.
    Use the 'append' function to add the details to it. However, those details
    will be dataase entries themselves. This is the classic debate, few large
    documents vs lots of small documents."""
    # Obtain the highest "my_id" code already registered.
    # Get a list of all the registered base-36 codes
    xParam = {}
    xRestr = {"_id":0, "my_id":1}
    cLine = db.lines(ccTremb)
    dId_query = cLine.find(xParam, xRestr)
    iHighest, aEvery_id = misc.find_highest_id(dId_query)

    if(True):   # Debugging
        sTxt = "\n\nHighest number is {0}(10) < < < < < < < <"
        print(sTxt.format(iHighest))

    # We do have the highest identifier (expressed as a decimal number). Hence,
    # we can incerement the sequence and use it.
    iNext_id = iHighest + 1
    if iNext_id > 36**5:
        print("\n\aMaximum count has been exceeded")
        return None

    # Convert to base36
    sBase36 = misc.base_conv(iNext_id)
    sBase36_5 = sBase36.rjust(5, "0")
    # "0002W" -> "D00-02W"
    sNew_id = "K{0}-{1}".format(sBase36_5[:2], sBase36_5[2:])

    # Display the number
    print("\nCode assigned will be: '{0}'".format(sNew_id))

# PREPARE THE TEMPLATE
    # Open a blank dictionary. I need to arrange the elements in order
    dNew_line = {
        "my_id":sNew_id,        # K00-001
        "tag":"meta",           # Describes that this is the description
        "dVal":{
            "host_geo_code":None,   # VA
            "route_no":None,        # RFU for road B96
            "sRoute_name":"",       # "Vænesston-Kændis Beach (VA-FS)"
            "type":None,            # RFU
            "start":None,           # Where is the zero km count
            "end":None,             # Where is the maximum point
        } # Closes "dVal" for the meta data
    }

# GET THE HOST:
    sTxt = ("\n\nPlease note that an unregistered host may be entered. Fill " +
             "out the known part\nof the geocode. Enter '?' as the final " +
             "character. Geocode will not be verified.\nIt will be entered as "+
             "'Unnamed'" +
             "\n\nPlease enter the geo-code of the Host:")
    print(sTxt)
    sGeo_code = input().upper()

    # Confirm host exists
    if sGeo_code[-1] != "?":
        cDest = db.destinations(ccTremb)
        aHost_name = misc.verify_geo_code(sGeo_code, cDest)
        if aHost_name == None:
            print("\n\aUnrecognised host name. Exiting")
            return
        sTxt = "\nHosted by {0} / {1}"
        print(sTxt.format(aHost_name["lat"], aHost_name["cyr"]))

    # Save the geocode
    dNew_line["dVal"]["host_geo_code"] = sGeo_code

# ROUTE NUMBER
    sTxt = "Is the route number (Б96 for example) known?"
    yn_route = misc.get_binary(sTxt)
    if yn_route == "Y":
        sTxt = "\nPlease enter the route number:"
        dNew_line["dVal"]["route_no"] = input().upper()
    else:
        dNew_line["dVal"]["route_no"] = None

# NAME OF THE STRETCH
    sTxt = ("\nPlease enter the name of this stretch. For example:\n" +
            "Vænesston-Kændis Beach (VA-FS)")
    print(sTxt)
    dNew_line["dVal"]["sRoute_name"] = input()

# TODO: TYPE OF LINE

# STARTING POINT
    sTxt = "\nIs the STARTING point known?"
    yn_start = misc.get_binary(sTxt)
    if yn_start == "Y":
        sTxt = ("\nWhere is the starting point? (Ex: 'VAA-00', "+
                "'K00-001@km0.00')")
        print(sTxt)
        dNew_line["dVal"]["start"] = input()
    else:
        print("TODO 'AXUZI'")
        return None

# FINISHING POINT
    sTxt = "\nIs the ENDING point known?"
    yn_end = misc.get_binary(sTxt)
    if yn_end == "Y":
        sTxt = ("\nWhere is the ending point? (Ex: 'FS0', 'K00-001@km0.00')")
        print(sTxt)
        dNew_line["dVal"]["start"] = input()
    else:
        print("TODO 'BZHAK'")
        return None

# Meta data captured:
    cLine.insert_one(dNew_line)
    print(">>>\nNew line OPENED")

#-------------------------------------------------------------------------------
# 3. Pretty print one line
#-------------------------------------------------------------------------------
def pretty_print_all(ccTremb):
    """ Writes to a file the full line, ordered by km"""

    import datetime

    sTxt = "\nEnter the line identifier ('K00-001') to be printed"
    print(sTxt)
    sK_code = input().upper()

# Verify the existance of the route
    sRte_det = qVerify_line(sK_code, ccTremb)
    if sRte_det == None: return None    # Error condition

# Extract the full data
    cLine = db.lines(ccTremb)
    xParam = {"my_id":sK_code, "tag":"val"}
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)
    dQuery.sort("dVal.km")

# Extract the data
    dData = []
    for query in dQuery:
        dData.append(query)       # Save data for further processing

    sFile_path = "Logs/{0}_full.txt".format(sK_code)
    eSingle_data = open(sFile_path, "w", encoding = "utf-8")

    sAll = ""               # All data in a single string.
# Write the title:
    xNow = datetime.datetime.now()

    sTxt = "Pretty print information for was generated on {0}\n".format(xNow)
    sAll += sTxt
    sAll += sRte_det + "\n"        # Populated by the route verification function

    for dItem in dData:
        sTxt = "{0:7.2f}km ".format(dItem["dVal"]["km"])
        sTxt += "[id:{0:>4}] ".format(dItem["dVal"]["id"])
        sTxt += "{0}: ".format(dItem["dVal"]["item"]).upper()
        sTxt += "{0} ".format(dItem["dVal"]["type"])
        sTxt += " --> {0}".format(dItem["dVal"]["xVal"])

        sAll += sTxt + "\n"

# Write the data to the file
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()


#-------------------------------------------------------------------------------
# 4. Pretty print the meta data to a file
#-------------------------------------------------------------------------------
def pretty_print_meta(ccTremb):
    """ Writes elements of the meta-data entry to a file """

    import datetime

    sTxt = "\nEnter the line identifier ('K00-001') to be printed"
    print(sTxt)
    sK_code = input().upper()

# Access database
    cLine = db.lines(ccTremb)
    xParam = {"my_id":sK_code, "tag":"meta"}
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)

# Extract the data
    dData = ""
    for query in dQuery:
        dData = query       # Save data for further processing

    if dData == "":
        print("\n\aNo information available")
        return None

    sFile_path = "Logs/{0}_meta.txt".format(sK_code)
    eSingle_data = open(sFile_path, "w", encoding = "utf-8")

    sAll = ""               # All data in a single string.
# Write the title:
    xNow = datetime.datetime.now()

    sTxt = "Pretty print information was generated on {0}\n".format(xNow)
    sAll += sTxt

    sAll += "METADATA:\n"
    dVal = dData["dVal"]
    sAll += ">   Host Geo-code: '{0}'\n".format(dVal["host_geo_code"])
    sAll += ">   Route number:  '{0}'\n".format(dVal["route_no"])
    sAll += ">   Route name:    '{0}'\n".format(dVal["sRoute_name"])
    sAll += ">   Type of line:  '{0}'\n".format(dVal["type"])
    sAll += ">   Starting point:'{0}'\n".format(dVal["start"])
    sAll += ">   Ending point:  '{0}'\n".format(dVal["end"])
    print(dData)

# Write the data to the file
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()

#-------------------------------------------------------------------------------
# 5. Add sub-component to line
#-------------------------------------------------------------------------------
def add_sub_comp(ccTremb):
    """ This method adds to the railway line opened. Items line track switches,
    level crossings, diverges, merges, stations, ect can be added.
    """
# Get the line input.
    # To avoid annoying the user of having to enter the line segment, lets
    # assume that the user is working on the 'latest' line. So, lets provide
    # the preselected item.
    xParam = {}
    xRestr = {"_id":0}
    cLine = db.lines(ccTremb)
    dId_query = cLine.find(xParam, xRestr).sort("_id",-1)
    dId_query.sort("_id", -1)   # From latest to earliest

    # Pull the text for the user to know if he is working on the correct object
    sCode = dId_query[0]["my_id"]

    sTxt = ("The last worked on line was '{0}'. Would you like to work on"+
    " it more?").format(sCode)
    yn_prev_code = misc.get_binary(sTxt)
    if yn_prev_code == "N":
        print("Please enter the line code (K00-001) you would like to work on")
        sLast_code = input().upper()

# Verify the existance of the code and return a string verifying identity
    sRte_det = qVerify_line(sCode, ccTremb)
    if sRte_det == None: return None    # Error condition

# Full confirmation message:
    sTxt = ("Are you are working on {0}".format(sRte_det))
    yn_confirm = misc.get_binary(sTxt)
    if yn_confirm == 'N': return

# Confirmation completed. Lets get the reference point
    # Run a query on all milestones.
    xParam = {"my_id":sCode, "tag":"val"}
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)

    dData = []
    for query in dQuery:
        dData.append(query)       # Save data for further processing

    # Pull out the distances already entered
    s1st_line = "Enter the relative distance from the last known point"
    sMenu = "{0}:\n".format(s1st_line)
    sMenu += "0  : -.--km (beginning of the line)\n"
    iNo_of_entries = len(dData)
    iIndex = 0

    # pull out the reference numbers
    iHighest = 0

    # Offer the distances in a menu
    for idx in range(iNo_of_entries):
        iIndex += 1         # This will show up in the menu.
        sLast_item = ""
        dItem = dData[idx]["dVal"]
        sLast_item += "{:.2f}km ".format(dItem["km"])
        sLast_item += "({0}-".format(dItem["item"])
        sLast_item += "{0}-".format(dItem["type"])
        sLast_item += "{0})".format(dItem["xVal"])
        iLoc_high = dItem["id"]
        if iLoc_high > iHighest:
            iHighest = iLoc_high

        sMenu += ("{0:<3}: {1}".format(iIndex, sLast_item))[:78] + "\n"
            # Keep the string less than 78 characters (avoid collumn breaks)

    # Get the user to choose.
    iDist_choice = misc.get_int(sMenu, iIndex)
    if iDist_choice == None:
        return

    # Default option, when there is no other options.
    fDist = 0.00
    if iDist_choice != 0:
        sTxt = "Is the absolute distance known (from 0.00km)?"
        yn_abs_dist = misc.get_binary(sTxt)
        if yn_abs_dist == "Y":
            sTxt = "Please enter the absolute distance in km"
            fAbs_dist = misc.get_float(sTxt) # Allow negative dist.
            if fAbs_dist == None: return
            fDist = round(fAbs_dist,2)
        # We want to enter a relative distance
        else:
            sTxt = "Is the relative distance read from the map?"
            yn_rel_map = misc.get_binary(sTxt)
            if yn_rel_map == "N":
                # Relative distance is known in km.
                sTxt = "Please enter the relative distance in km"
                fRel_dist = misc.get_float(sTxt, bNeg=True)
                if fRel_dist == None: return
                fRel_dist = round(fRel_dist,2)
            # We are reading off the map.
            else:
                # Select a map to work on
                dMap = misc.get_the_map(ccTremb)
                if dMap == None:
                    print("\n\aInvalid map selected. Exiting")
                    return None
                fScale = dMap["fScale"]

                # Ask user to input the distance on the map.
                sTxt = "Please enter the relative distance in mm from the map"
                fRel_mm = misc.get_float(sTxt, bNeg=True)
                if fRel_mm == None: return

                fRel_dist = fRel_mm * (fScale / 1e6) # Convert map mm to km
                fRel_dist = round(fRel_dist, 2)
                print("km distance: {0}".format(fRel_dist))
            # Relative distane known. Now calculate the absolute distance
            iEntry = iDist_choice - 1       # 1-count to 0-count
            fOld_dist = dData[iEntry]["dVal"]["km"]
            fDist = fOld_dist + fRel_dist
            fDist = round(fDist, 2)
        # Absolute distance is now known.
    # Non-initial condition is being closed here.

    sMenu = "\nPlease select 'event' category:\n"
    sMenu += "1.  Build Track\n"
    sMenu += "2.  Build Junction\n"
    sMenu += "3.  Station\n"
    sMenu += "4.  Non-rail crossing\n"
    sMenu += "5.  [RFU] --- Structure\n"
    sMenu += "6.  Elevation\n"
    sMenu += "7.  [RFU] --- Signal\n"
    sMenu += "8.  Sign (speed / warning / direction)"
    print(sMenu)
    sInput = input().upper()

    dPack = {
        "tremb": ccTremb,           # For full DB access.
        "db": cLine,
        "dEntry": {
            "km":fDist,
            "id":iHighest+1,        # Unique reference number
            "item":None,
            "type":None,
            "xVal":None},
    }

    if sInput == "1":
        dEntry = qEvent_track(dPack)
    elif sInput == "2":
        dEntry = qEvent_junction(dPack)
    elif sInput == "3":
        dEntry = qEvent_station(dPack)
    elif sInput == "4":
        dEntry = qEvent_crossing(dPack)
    elif sInput == "6":
        dEntry = qEvent_elevation(dPack)
    elif sInput == "8":
        dEntry = qEvent_signage(dPack)
    else:
        print("\n\aInvalid selection. Exiting")
        return

    if dEntry == None: return   # We got an error somewhere.

    # Add the item to the database
    dAdd_line = {
        "my_id":sCode,              # K00-001
        "tag":"val",                # Describes that this is the description
        "dVal":dEntry,              # The data generated
    }

    sTxt = "Is this entry OK?: \n{0}\n".format(dAdd_line)
    yn_final = misc.get_binary(sTxt)
    if yn_final == "N":
        print("User confirmation declined. Exiting")
        return

    # Add to the data base.
    cLine.insert_one(dAdd_line)
    print(">>>\nNew item added")

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 1: Track
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
def qEvent_track(dPack):
    """ This function builds up a piece of track for us.
        dPack = {
            "tremb": ccTremb,           # For full DB access.
            "db": cLine,                # Database entries for the line.
            "dEntry": {                 # This parameter will be passed back
                "km":fDist,             # kmilage marker
                "id":iHighest+1,        # Unique reference number
                "item":None,            # We need to fill this with our data
                "type":None,            # We need to fill this with our data
                "xVal":None},           # We need to fill this with our data
        }
"""

    dEntry = dPack["dEntry"]        # Unpack the prototype
    sMenu = ("The observer is looking away from the point 'km:0.00'. Hence, "+
        "'start', 'end',\n'merge', 'diverge', 'left', 'right' are biased. "+
        "'track:n' is after the track\nevent. Tracks are numbered '1' to 'n' "+
        "left to right\n\n")
    sMenu += "Select track event:\n"
    sMenu += "0   Comment (record something unusual)\n"
    sMenu += "1   Start tracks (Terminus if at km:0.00)\n"
    sMenu += "2   [RFU]   End tracks (dead-end / Storage)\n"
    sMenu += "3   Merge tracks (4 to 1 for example)\n"
    sMenu += "4   Diverge tracks (1 to 4 for example)\n"
    sMenu += "5   IXI-junction (Simultaneous bi-direct. 'lane change')\n"
    sMenu += "6   [RFU]   Rail-to-rail level crossing\n"
    sMenu += "7   [RFU]   Join two lines head-on (at a border)\n"

    print(sMenu)
    sInput = input().upper()

# COMMENTS
    if sInput == "0":   # Comment
        dEntry["item"] = "track"
        dEntry["type"] = "comment"    # Type of transaction
        sTxt = "Please enter a comment regarding track"
        print(sTxt)
        dEntry["xVal"] = input()
        return dEntry

# START OF TRACK
    if sInput == "1":   # Start tracks
    #"dEntry":{"km":fDist,"tracks":0,"item":None,"type":None,"xVal":None},

        # Terminus question:
        if dEntry["km"] < 0.001:        # Beginning of the line from a terminus
            sTxt = "Please enter number of tracks that are starting:"
            iNew_tracks = misc.get_int(sTxt)
            if iNew_tracks == None: return None

            dEntry["item"] = "track"
            dEntry["type"] = "start_all"
            dEntry["xVal"] = iNew_tracks
        else:
            print("TODO")
            return None
        return dEntry

    if sInput == "2":   # End tracks
        print("TODO")

    if sInput == "3":   # Merge tracks
        sTxt = "Please confirm number of tracks BEFORE merger:"
        iBef = misc.get_int(sTxt)
        if iBef == None: return None

        sTxt = "Please enter number of tracks AFTER merger:"
        iAft = misc.get_int(sTxt)
        if iAft == None: return None

        dEntry["item"] = "track"
        dEntry["type"] = "merge"
        xVal = {"iBef": iBef, "iAft": iAft}
        dEntry["xVal"] = xVal
        return dEntry

    if sInput == "4":   # Diverge tracks
        sTxt = "Please confirm number of tracks BEFORE divergence:"
        iBef = misc.get_int(sTxt)
        if iBef == None: return None

        sTxt = "Please enter number of tracks AFTER divergence:"
        iAft = misc.get_int(sTxt)
        if iAft == None: return None

        dEntry["item"] = "track"
        dEntry["type"] = "diverge"
        xVal = {"iBef": iBef, "iAft": iAft}
        dEntry["xVal"] = xVal
        return dEntry

    if sInput == "5":   # IXI-junction: Allows for changes between tracks.
            # Simultaneous merge then diverge. Imagine that all the 'legs' of
            # the letters are tracks. They would form the prase "IXI"
        sTxt = "Please confirm number of tracks in 'IXI' junction:"
        iIxi = misc.get_int(sTxt)
        if iIxi == None: return None

        dEntry["item"] = "track"
        dEntry["type"] = "ixi"
        xVal = {"iBef": iIxi, "iAft": iIxi}
        dEntry["xVal"] = xVal
        return dEntry


    if sInput == "6":   # Rail-to-rail level crossing
        print("TODO")

    else:
        print("\n\aInvalid selection. Exiting")
        return None

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 2: Junction
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

def qEvent_junction(dPack):
    """ Method allows for other lines to join us. I have decided against using
    anonymous links. I have 60M lines available, so I don't have to save.
        dPack = {
            "tremb": ccTremb,           # For full DB access.
            "db": cLine,                # Database entries for the line.
            "dEntry": {                 # This parameter will be passed back
                "km":fDist,             # kmilage marker
                "id":iHighest+1,        # Unique reference number
                "item":None,            # We need to fill this with our data
                "type":None,            # We need to fill this with our data
                "xVal":None},           # We need to fill this with our data
        }
"""

    dEntry = dPack["dEntry"]        # Unpack the prototype
    sMenu = ("Please select the junction event from the list")
    sMenu += "Select track event:\n"
    sMenu += "0   Comment (record something unusual)\n"
    sMenu += "1   Spliting from us (Normal 'Y')\n"
    sMenu += "2   Joining us (Up-side-down 'Y' or 'λ')\n"

    print(sMenu)
    sInput = input().upper()

# COMMENT
    if sInput == "0":   # Comment
        dEntry["item"] = "junction"
        dEntry["type"] = "comment"    # Type of transaction
        sTxt = "Please enter a comment regarding station"
        print(sTxt)
        dEntry["xVal"] = input()
        return dEntry

# REGISTERED HOST
    if sInput == "1":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "junction"
        dEntry["type"] = "split"    # Type of transaction
        sTxt = "Please enter the 'K-code' of line spliting (ex. 'K00-002')"
        print(sTxt)
        sK_code = input().upper()

        sTxt = "Is this is the 'far-end' (km > 0) of the line?"
        yn_far_end = misc.get_binary(sTxt)
        if yn_far_end == None: return None
        if yn_far_end == "Y":
            sTerminus = "far_end"
        else:
            sTerminus = "home_end"

        xVal = {"line":sK_code, "terminus":sTerminus}
        dEntry["xVal"] = xVal
        return dEntry

# APPROXIMATE HOST
    if sInput == "2":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "junction"
        dEntry["type"] = "join"    # Type of transaction
        sTxt = "Please enter the 'K-code' of line joining (ex. 'K00-002')"
        print(sTxt)
        sK_code = input().upper()

        sTxt = "Is this is the 'far-end' (km > 0) of the line?"
        yn_far_end = misc.get_binary(sTxt)
        if yn_far_end == None: return None
        if yn_far_end == "Y":
            sTerminus = "far_end"
        else:
            sTerminus = "home_end"

        xVal = {"line":sK_code, "terminus":sTerminus}
        dEntry["xVal"] = xVal
        return dEntry

    else:
        print("\n\aInvalid selection. Exiting")
        return None

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 3: Station
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
def qEvent_station(dPack):
    """ This function builds up a piece of station for us.
        dPack = {
            "tremb": ccTremb,           # For full DB access.
            "db": cLine,                # Database entries for the line.
            "dEntry": {                 # This parameter will be passed back
                "km":fDist,             # kmilage marker
                "id":iHighest+1,        # Unique reference number
                "item":None,            # We need to fill this with our data
                "type":None,            # We need to fill this with our data
                "xVal":None},           # We need to fill this with our data
        }
"""

    dEntry = dPack["dEntry"]        # Unpack the prototype
    sMenu = ("Please select the station event from the list")
    sMenu += "Select track event:\n"
    sMenu += "0   Comment (record something unusual)\n"
    sMenu += "1   Registered host:   (geo_code is known)\n"
    sMenu += "2   Approximate host: (geo_code not verified)\n"

    print(sMenu)
    sInput = input().upper()

# COMMENT
    if sInput == "0":   # Comment
        dEntry["item"] = "station"
        dEntry["type"] = "comment"    # Type of transaction
        sTxt = "Please enter a comment regarding station"
        print(sTxt)
        dEntry["xVal"] = input()
        return dEntry

# REGISTERED HOST
    if sInput == "1":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "station"
        dEntry["type"] = "geo_code"    # Type of transaction
        sTxt = "Please enter the geo_code of the station's host:"
        print(sTxt)
        sGeo_code = input().upper()

        # Verify existance of this geo-code
        cDest = db.destinations(dPack["tremb"]) # Wrapper for 'ccTremb'
        aName = misc.verify_geo_code(sGeo_code, cDest)
        if aName == None: return None   # verification failed

        xVal = {
            "geo":sGeo_code,
            "lat":aName["lat"],
            "cyr":aName["cyr"]
            }
        dEntry["xVal"] = xVal
        return dEntry

# APPROXIMATE HOST
    if sInput == "2":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "station"
        dEntry["type"] = "approx"    # Type of transaction
        sTxt = ("Please enter the APPROXIMATE geo_code of the station's host:"+
            " \n'? are allowed, code will not be verified")
        print(sTxt)
        sApprox_code = input().upper()

        sTxt = ("Please enter a description, if available")
        sDesc = input()

        xVal = {
            "code":sApprox_code,
            "desc":sDesc,
            }
        dEntry["xVal"] = xVal
        return dEntry

    else:
        print("\n\aInvalid selection. Exiting")
        return None

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 3: Crossing
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
def qEvent_crossing(dPack):
    """ This function builds up a piece of station for us.
        dPack = {
            "tremb": ccTremb,           # For full DB access.
            "db": cLine,                # Database entries for the line.
            "dEntry": {                 # This parameter will be passed back
                "km":fDist,             # kmilage marker
                "id":iHighest+1,        # Unique reference number
                "item":None,            # We need to fill this with our data
                "type":None,            # We need to fill this with our data
                "xVal":None},           # We need to fill this with our data
        }
"""

    dEntry = dPack["dEntry"]        # Unpack the prototype
    sMenu = ("Please select the station event from the list")
    sMenu += "Select track event:\n"
    sMenu += "0   Comment (record something unusual)\n"
    sMenu += "1   River (bridge or tunnel)\n"

    print(sMenu)
    sInput = input().upper()

# COMMENT
    if sInput == "0":   # Comment
        dEntry["item"] = "crossing"
        dEntry["type"] = "comment"    # Type of transaction
        sTxt = "Please enter a comment regarding station"
        print(sTxt)
        dEntry["xVal"] = input()
        return dEntry

# REGISTERED HOST
    if sInput == "1":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "crossing"
        dEntry["type"] = "river"    # Type of transaction

        sTxt = "Please enter the name of the river being crossed:"
        print(sTxt)
        sName = input()

        sTxt = "Please enter approximate width of the river in integer meters"
        iWidth = misc.get_int(sTxt)
        if iWidth == None: return None

        xVal = {
            "sName":sName,
            "iWidth":iWidth,
            }
        dEntry["xVal"] = xVal
        return dEntry


    else:
        print("\n\aInvalid selection. Exiting")
        return None


#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 6: Elevation
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
def qEvent_elevation(dPack):
    """ Method caters for recording of change in gradient.
    dPack = {
        "tremb": ccTremb,           # For full DB access.
        "db": cLine,                # Database entries for the line.
        "dEntry": {                 # This parameter will be passed back
            "km":fDist,             # kmilage marker
            "id":iHighest+1,        # Unique reference number
            "item":None,            # We need to fill this with our data
            "type":None,            # We need to fill this with our data
            "xVal":None},           # We need to fill this with our data
    }
    """

    dEntry = dPack["dEntry"]        # Unpack the prototype
    sMenu = ("Please select the elevation event from the list\n")
    sMenu += "Select track event:\n"
    sMenu += "-   [Comments not allowed here. Technical reasons]\n"
    sMenu += "1   Record spot height\n"
    sMenu += ("2   Trapezoidal change (_/TT\_). (!)"+
                " Req. All 4 pts in km seq. (!)\n")

    print(sMenu)
    sInput = input().upper()

# COMMENT
    if sInput == "0":   # Comment
        print("Comments not allowed for 'elevation events'")
        return None

# SPOT ELEVATION
    if sInput == "1":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "elev_ft"
        dEntry["type"] = "spot"    # Type of transaction
        sTxt = "Please enter spot elevation, (in ft), as an integer"
        iSpot = misc.get_int(sTxt, bNeg=True)
        dEntry["xVal"] = iSpot
        return dEntry

# TRAPEZIODAL ELEVATION _/TT\_
    if sInput == "2":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "elev_ft"
        dEntry["type"] = "trapezoid"    # Type of transaction
        sTxt = ("Please enter the local change of elevation, (in ft), " +
            "as an integer.\n(Example '0' or '-20')")
        iSpot = misc.get_int(sTxt, bNeg=True)
        dEntry["xVal"] = iSpot
        return dEntry



    else:
        print("\n\aInvalid selection. Exiting")
        return None

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# 8: Signage
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
def qEvent_signage(dPack):
    """ This function sets up a 'trafic sign'.
    dPack = {
        "tremb": ccTremb,           # For full DB access.
        "db": cLine,                # Database entries for the line.
        "dEntry": {                 # This parameter will be passed back
            "km":fDist,             # kmilage marker
            "id":iHighest+1,        # Unique reference number
            "item":None,            # We need to fill this with our data
            "type":None,            # We need to fill this with our data
            "xVal":None},           # We need to fill this with our data
    }
    """

    dEntry = dPack["dEntry"]        # Unpack the prototype
    sMenu = ("Please select the station event from the list")
    sMenu += "Select track event:\n"
    sMenu += "0   Comment (record something unusual)\n"
    sMenu += "1   Speed limit, dir: 'away' (increasing km-count)\n"
    sMenu += "2   Speed limit, dir: 'home' (decreasing km-count)\n"


    print(sMenu)
    sInput = input().upper()

# COMMENT
    if sInput == "0":   # Comment
        dEntry["item"] = "sign"
        dEntry["type"] = "comment"    # Type of transaction
        sTxt = "Please enter a comment regarding station"
        print(sTxt)
        dEntry["xVal"] = input()
        return dEntry

# SPEED AWAY
    if sInput == "1":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "sign"
        dEntry["type"] = "speed_away"    # Type of transaction
        sTxt = "Please enter speed limit going away in km/h:"
        iKmh = misc.get_int(sTxt)
        if iKmh == None: return     # Error handling
        xVal = {                    # For synchronisation with other signs
            "val":iKmh,
            "dis":None,
            "dur":None
            }
        dEntry["xVal"] = xVal
        return dEntry

# SPEED HOME
    if sInput == "2":
    #"dEntry":{"km":fDist,"id":0,"item":None,"type":None,"xVal":None},
        dEntry["item"] = "sign"
        dEntry["type"] = "speed_home"    # Type of transaction
        sTxt = "Please enter speed limit coming home in km/h:"
        iKmh = misc.get_int(sTxt)
        if iKmh == None: return     # Error handling
        xVal = {                    # For synchronisation with other signs
            "val":iKmh,
            "dis":None,
            "dur":None
            }
        dEntry["xVal"] = xVal
        return dEntry

    else:
        print("\n\aInvalid selection. Exiting")
        return None

#-------------------------------------------------------------------------------
# 6. GRADIENT REPORT
#-------------------------------------------------------------------------------
def q_grad_calc(fKm_now, fKm_bef, fFt_now, fFt_bef):
    """ Method does the actual calculation of taking the horizonal difference
    and the vertical difference. It will return a structure containing those
    sub-results as well as the gradient in percent and 1:x formats. NOTE that
    flat gradient is 1:9999
    """
    # Calculate the change in distance
    fDelta_km = round(fKm_now - fKm_bef, 2)
    fHoriz_m = round(fDelta_km * 1000.0, 1) #
    if fHoriz_m <= 0:
        sTxt = ("\n\aDistances not in order OR vertical wall")
        return None

    # Calculate the change in elevation
    fDelta_ft = round(fFt_now - fFt_bef, 2)
    fVert_m = round(fDelta_ft * 0.3048, 1)

    # Calculate the %-expression
    fPercent = round(fVert_m * 100 / fHoriz_m, 2)

    # Calculate the 1:__ expression
    fFactor = None
    if fVert_m == 0:
        fFactor = 9999.0          # Infinity approximation
    else:
        fFactor = round(fHoriz_m / fVert_m, 1)
        if fFactor > 9999.0: fFator = 9999.0

    # Present the data:
    dItem = {
        "type"  : None,
        "km_bef": fKm_bef,
        "km_now": fKm_now,
        "km_del": fDelta_km,
        "ft_bef": fFt_bef,
        "ft_now": fFt_now,
        "ft_del": fDelta_ft,
        "percent": fPercent,
        "one_in": fFactor
    }
    return dItem
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

def qLine_gradient(sK_code, ccTremb):
    """ Method takes in the 'K-code' (K00-001) for Vænesston - Fusþton Line.
    It then extracts the elevation information and computes the grade of the
    track.
    """
# Access database
    cLine = db.lines(ccTremb)

# K-CODE EXISTS?:
    cLine = db.lines(ccTremb)
    xParam = {"my_id":sK_code, "tag":"meta"}
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)

    # Extract the data
    dMeta = ""
    for query in dQuery:
        dMeta = query       # Save data for further processing

    if dMeta == "":
        print("\n\aLine does not exist")
        return None

# EXTRACT THE DATA
    xParam = {"my_id":sK_code,  # Only this line
              "tag":"val",      # Only true data
              "dVal.item":"elev_ft" # Only elevation data.
              }
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)
    dQuery.sort("dVal.km")

# Extract the data
    dRaw = []
    for query in dQuery:
        dRaw.append(query)       # Save data for further processing

    # my_id and tag have been assured by the database query. extract the
    # 'interesting' stuff.
    dData = []
    for item in dRaw:
        dItem = {
            "km": item["dVal"]["km"],
            "type": item["dVal"]["type"],
            "elev_ft": item["dVal"]["xVal"]
            }
        dData.append(dItem)

    # misc.write_debug_txt(dData)         # See what we found

    # Prepare for calculation:
    dGradient = []
    iNo_of_items = len(dData)           # Working in pairs of values.

# TERRAIN:
    for iCnt in range(1, iNo_of_items):
        # Process the spot elevation first.
        if dData[iCnt]["type"] != "spot":    # spot elevation, not trapezoidal
            continue                        # Loop to the next iteration.

    # LOOK FOR THE PREVIOUS 'SPOT' HEIGHT.
        # We are a spot. Lets look back to find the previous spot.
        iPrev_spot_idx = None           # Either next or 5 back... read on

        # There could be a bridge or tunnel behind us. Also, there could be
        # an error in its entry. At this stage, we don't care. We just want
        # to find the last spot height.
        for iIdx in range(iCnt-1, -1, -1):        # Go backwards
            if dData[iIdx]["type"] == "spot":
                iPrev_spot_idx = iIdx
                break

        if iPrev_spot_idx == None:
            print("\n\aERROR: Unable to find previous spot height")
            return None

    # DO THE CALCULATION
        fKm_now = dData[iCnt]["km"]
        fKm_bef = dData[iPrev_spot_idx]["km"]
        fFt_now = dData[iCnt]["elev_ft"]
        fFt_bef = dData[iPrev_spot_idx]["elev_ft"]

        # Calculation is common to 'terrain' and 'structure' items.
        dItem = q_grad_calc(fKm_now, fKm_bef, fFt_now, fFt_bef)
        dItem["type"] = "Terrain"
        dGradient.append(dItem)
    # End of the elevation loop loop

# BRIDGES AND TUNNELS:
    # Run the bridges and tunnels as a second pass.
    for iCnt in range(iNo_of_items):
        if dData[iCnt]["type"] != "trapezoid":
            continue                        # Loop to the next iteration.

        iExam = iCnt + 0
        if dData[iExam]["elev_ft"] == 0:    # Beginning or End of a structure
            # Test for beginning: look at the previous item
            iExam = iCnt - 1

            # Does the previous item exist?
            if iExam < 0:
                sError = ("\n\aERROR: Structure needs a preceeding "+
                    "'spot elevation' for correct operation\n")
                print(sError)
                return None

            bBegin = False
            # Test if this is the first structure after a spot height
            if dData[iExam]["type"] == "spot":
                bBegin = True

            # Test if the previous structure was terminated
            if(dData[iExam]["type"] == "trapezoid" and
               dData[iExam]["elev_ft"] == 0):
               bBegin = bBegin or True

            # We have a beginning of a structure.
            if bBegin:
                # VERIFY ELEMENTS IN SUB-STRUCTURE (0, [+20, +20, 0])
                for iOffset in range(1, 4):
                    # There are
                    iExam = iCnt + iOffset    # Look forwards at the data
                    if iExam >= iNo_of_items:
                        sError = ("\n\aERROR: Structure has suddenly ended " +
                            "(listing error)\n")
                        print(sError)
                        return None

                    if (dData[iExam]["type"] != "trapezoid"):
                        # Wrong type
                        sError = ("\n\aERROR: Structure has suddenly ended " +
                            "(non-structural item found as a next element)\n")
                        print(sError)
                        return None

                    if iOffset in [1, 2] and dData[iExam]["elev_ft"] == 0:
                        sError = ("\n\aERROR: Structure's central 'span' is " +
                        "not elevated or depressed. Expected non-zero number")
                        print(sError)
                        return None

                    if iOffset == 3 and dData[iExam]["elev_ft"] != 0:
                        sError = ("\n\aERROR: Structure has no termination")
                        print(sError)
                        return None
                # End going through the next 3 following points of the structure

            # CALCULATE THE ACTUAL ELEVATIONS AT ALL THE 4 SPOTS:
                # Lets use the previous calculations which generated a list
                # of dictionaries named 'dGradient'. Lets look through it and
                # try to find the piece of terrain we are working on.
                iIdx = None                 # Entry pointer w/ error detect
                km_tgt = dData[iCnt]["km"]  # Our target milepost
                for dItem in dGradient:
                    if (dItem["km_bef"] < km_tgt < dItem["km_now"] and
                        dItem["type"] == "Terrain"):
                        iIdx = dGradient.index(dItem)
                        break

                if iIdx == None:
                    sTxt = ("\n\aERROR: Unable to find host terrain section.")
                    return None

                # Calculate ft/km gradient. This gives us both units.
                dTerrain = dGradient[iIdx]          # Extract the entry
                fFt_per_km = dTerrain["ft_del"] / dTerrain["km_del"]

                # distance from beginning of terrain setion to the structure
                # Initialisation of the loop:
                afFt = [0, 0, 0, 0]
                fKm_bef = dTerrain["km_bef"]

            # Calculate the equivalent 'spot' elevations
                for iOffset in range(4):
                # Build up the km
                    iNow = iCnt + iOffset
                    fKm_str = dData[iNow]["km"]              # Structure element
                    fLoc_km = round(fKm_str - fKm_bef, 2)    # Local km

                    # how much has the terrain changed upto our structure:
                    fFt_del = fLoc_km * fFt_per_km             # ft = km * ft/km

                    # What is the absolue elevation at the foot of the bridge?
                    # 1.) Use ratio and proportion to get the base of element.
                    fFt_terrain = dTerrain["ft_bef"] + fFt_del

                    # 2.) Add the relative change of the structure
                    fFt_struct = fFt_terrain + dData[iNow]["elev_ft"]

                    # 3.) Round off and save.
                    afFt[iOffset] = round(fFt_struct, 1)

                # Calculate the actual gradients of the structure
                for iCalc in range(1, 4):
                # DO THE CALCULATION
                    iNow = iCnt + iCalc - 0

                    fKm_now = dData[iNow-0]["km"]
                    fKm_bef = dData[iNow-1]["km"]
                    fFt_now = afFt[iCalc-0]
                    fFt_bef = afFt[iCalc-1]

                    # Calculation is common to 'terrain' and 'structure' items.
                    dItem = q_grad_calc(fKm_now, fKm_bef, fFt_now, fFt_bef)
                    dItem["type"] = "Structure"
                    dGradient.append(dItem)

            # End of finding the beginning of the structure
        # End of delta elevation is zero

    # All the bridges and tunnels have been sorted out. Lets sort the list
    dSorted = sorted(dGradient, key= lambda i: i["km_bef"])

    # Debug: to see what the track data actually looks like.
    return dSorted                    # Return the array of tracks.

#--------------------------------------------------------------
def pretty_gradient(ccTremb):
    """ Writes to a file elevation changes between mileposts, ordered by km.
    This function is the 'human interface' side. The actual worker function
    is also callable from software (when presenting to the simulation)
    """
# Prepare and save the input
    import datetime
    sTxt = "\nEnter the line identifier ('K00-001') to be gradiented"
    print(sTxt)
    sK_code = input().upper()

    sRte_det = qVerify_line(sK_code, ccTremb)
    if sRte_det == None: return None    # Error condition

# Do the calculation
    adGrd = qLine_gradient(sK_code, ccTremb)
    if adGrd == None: return None      # Error has occured

# Open the file
    sFile_path = "Logs/{0}_gradient.txt".format(sK_code)
    eSingle_data = open(sFile_path, "w", encoding = "utf-8")

    sAll = ""               # All data in a single string.
# Write the title:
    xNow = datetime.datetime.now()

    sTxt = "Pretty print information for was generated on {0}\n".format(xNow)
    sAll += sTxt
    sAll += sRte_det        # Route number and name

    for dItem in adGrd:
        sTxt = "[{0}] km {1} to {2} "
        sTxt = sTxt.format(dItem["type"], dItem["km_bef"], dItem["km_now"])
        sAll += sTxt

        sTxt = "with {0}ft to {1}ft\n"
        sTxt = sTxt.format(dItem["ft_bef"], dItem["ft_now"])
        sAll += sTxt

        sTxt = ">   rise of {0}ft over {1}km\n"
        sAll += sTxt.format(dItem["ft_del"], dItem["km_del"])

        sTxt = ">   = {0}% slope or (1:{1}),   1:9999.0 means level\n"
        sAll += sTxt.format(dItem["percent"], dItem["one_in"])
        sAll += "\n"

# Write the data to the file
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()

#-------------------------------------------------------------------------------
# C. DESIGN A GRADIENT
#-------------------------------------------------------------------------------
def design_gradient(ccTremb):
    """ Method prompts the user for data and returns distance on the map for the
        approach to the structure.
    """
    dMap = misc.get_the_map(ccTremb)
    if dMap == None:
        print("\n\aInvalid map choice. Returning")
        return None
    fScale = dMap["fScale"]

    # Ask for the desired gradient
    sTxt = "Enter the desired gradient as 1:x (rail std is 100, highway: 33)"
    fHoriz_per_Vert = misc.get_float(sTxt)
    if fHoriz_per_Vert == None: return None

    # Ask for the elevation change
    sTxt = "Enter elevation change in feet, don't worry about the sign"
    fVert_ft = misc.get_float(sTxt)
    if fVert_ft == None: return None

    # Do the calculation
    fVert_m = fVert_ft * 0.3048
    fHoriz_m = fVert_m * fHoriz_per_Vert    # h = v * h/v (v's cancel)
    fPaper_m = fHoriz_m / fScale            # 2500m @ 1:1M = 0.0025m
    fPaper_mm = round(fPaper_m * 1000, 2)

    sAll =  "----------------------------\n"
    sAll +=  "{0}mm on the map are required\n".format(fPaper_mm)
    sAll += "----------------------------\n"
    sAll += "{0}ft(v) = {1:.1f}m(v)\n".format(fVert_ft, fVert_m)
    sTxt = "{0:.1f}m(h) = {1:.1f}m(v) * {2:.1f}m(h)/m(v)\n"
    sTxt = sTxt.format(fHoriz_m, fVert_m, fHoriz_per_Vert)
    sAll += sTxt
    sTxt = "{0}mm(p) = {1:.1f}m(h) / {2:.1f}m/m(scale)\n"
    sTxt = sTxt.format(fPaper_mm, fHoriz_m, fScale)
    sAll += sTxt
    print(sAll)

#-------------------------------------------------------------------------------
# _. REMOVE A COMPONENT
#-------------------------------------------------------------------------------
def remove_sub_comp(ccTremb):
    """ Method prompts the user for data and returns distance on the map for the
        approach to the structure.
    """
# Request the line identifier
    sTxt = ("You are about to remove a component from a line.\nPlease enter " +
        "the K-code ('K00-001' for example) of the line\n")
    print(sTxt)
    sK_code = input().upper()

# Verify the line number
    sRte_det = qVerify_line(sK_code, ccTremb)
    if sRte_det == None: return None

# Ask for the identifier mark
    sTxt = ("Please enter the item identifier (id: 39 for example) as an " +
        "integer")
    iId_req = misc.get_int(sTxt)
    if iId_req == None: return None

# Pull up the data you are about to delete:
    xParam = {"my_id": sK_code, "dVal.id":iId_req}
    xRestr = {"_id":0, "dVal":1}
    cDatabase = db.lines(ccTremb)
    dQuery = cDatabase.find(xParam, xRestr)

    dElement = []
    for query in dQuery:
        dElement.append(query)

    print("\n-----------------------------")
    sTxt = ("You are about to remove\n\n{0}\n\nfrom {1}\n\n" +
        "Do you want to procceed?")
    sTxt = sTxt.format(dElement[0], sRte_det)
    yn_remove = misc.get_binary(sTxt)
    if yn_remove == None: return None
    if yn_remove == "N":
        print("\n\aAborting removal")
        return None

    # Remove the item
    xParam = {"my_id": sK_code, "dVal.id":iId_req}
    xRestr = {}
    dQuery = cDatabase.delete_one(xParam, xRestr)
    print("Specified element deleted")

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
    cLine = db.lines(ccTremb)
    sSub_menu = """
LINES SUB-MENU (K):
.: Exit
1: Open New line (Record its meta-data)
3: Pretty print one line (ordered by distance)
4: Pretty print meta data to a file
5: Add to line (Sub-component as a new entry)
6: Do a gradient (elevation change) report
C: Calculate distance on map for gradient
_: Remove a sub-component from the line
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
