""" This file operates the 'destinations' sub-menu. Effectively, it accounts for
    the land mapped"""

import modules.x_database as db
import modules.x_misc as misc                            # For base36 conversion

#-------------------------------------------------------------------------------
# 1: ADD A NEW AREA
#-------------------------------------------------------------------------------
def add_area_to_db(ccTremb):
    """ This enters the process of adding a new area record to the database"""
    # Obtain the highest "my_id" code that is registered in the database.
    # NOTE: this is not safe. A destination may have been dropped. This would
    # cause a parent to have a wrong child registered.

    # Get a list of all the registered base-36 codes
    xParam = {}
    xRestr = {"_id":0, "my_id":1}
    cDest = db.destinations(ccTremb)
    dId_query = cDest.find(xParam, xRestr)
    iHighest, aEvery_id = misc.find_highest_id(dId_query)

    if(False):   # Debugging
        sTxt = "\n\nHighest number is {0}(10) < < < < < < < <"
        print(sTxt.format(iHighest))

    # Go through the children. We are trying to see if there are any missing
    # children. This would indicate a deleted identifier.
    xParam = {}
    xRestr = {"_id":0, "aChildren":1}
    dChild_query = cDest.find(xParam, xRestr)
    for dChildren in dChild_query:
        aChildren = dChildren["aChildren"]

        # We are only interested in geographics which do have children
        if len(aChildren) == 0:
            continue

        for child_my_id in aChildren:
            sBase36 = misc.clean_my_id(child_my_id)      # Remove the formatting
            iBase10 = int(sBase36, 36)
            if iBase10 > iHighest:
                sTxt = ("Unreferenced child found: registered with parent,"
                + " but has on entry for itself: {0}")
                print(sTxt.format(child_my_id))
                return None

        # Make sure that every 'child' has its own entry.
            if child_my_id not in aEvery_id:
                sTxt = ("A 'child' area was found which does not have"
                + " its own entry ({0})")
                print(sTxt.format(child_my_id))
                return None

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
    sNew_id = "D{0}-{1}".format(sBase36_5[:2], sBase36_5[2:])

# START GETTING THE USER TO ENTER THE NEW DATA.
    # Open a blank dictionary, so that the elements are arranged in a certain
    # order.
    dNew_area = {
        "my_id":sNew_id,
        "aName":{"lat":None, "cyr":None},
        "geo_code":None,
        "aType":{"lat":None, "cyr":None, "lvl":None},
        "sub_type":None,
        "parent":None,
        "aChildren":[],
        "aMap":{
            "sRegion":None,
            "iYear":None,
            "fScale":None,
            "x":None,
            "y":None,
            "a":None
        },
        "aArea":{"qty":None, "uom":None},
        "aDemand_workforce": {
            "total": {
                "rm": 0, "rf": 0, "hm": 0, "hf": 0, "mm": 0,
                "mf": 0, "lm": 0, "lf": 0, "pm": 0, "pf": 0},
            "aItemised": []},
        "aSupply_workforce": {"status":"RFU"},
# Initially designed, but never used.
#            "total": {
#                "rm": 0, "rf": 0, "hm": 0, "hf": 0, "mm": 0,
#                "mf": 0, "lm": 0, "lf": 0, "pm": 0, "pf": 0},
#            "aItemised": []},
        "aDemand_hholds": {
            "total": {"r": 0, "h": 0, "m": 0, "l": 0, "p": 0},
            "aItemised": []},
        "aSupply_hholds": {
            "total": {"r": 0, "h": 0, "m": 0, "l": 0, "p": 0},
            "aItemised": []},
        "aDemographics": {},
        "aVehicles": {},
        "aFootprint": {},
        "aWarehouse": {}
    }

# HARVEST THE DATA FROM THE USER.
    # Parent (who is above this area in the hierarchy)
    sTxt = ("\nEnter the 'geo_code' of the parent. "
    +" (example 'GYG', or 'i_am_world')")
    print(sTxt)

    sInput = input().upper()

    # Validate that the parent exists
    parent = sInput[:]          # Blank splice to make a copy
    xParam = {"geo_code":parent}
    xRestr = {"_id":0, "aName.lat":1, "my_id":1}
    dParent_query = cDest.find(xParam, xRestr)

    parent_my_id = ""
    if sInput != "I_AM_WORLD":
        iNo_of_parents = 0
        for dParent in dParent_query:
            iNo_of_parents += 1
            parent_my_id = dParent["my_id"]

        if iNo_of_parents != 1:
            sTxt = ("\nUnexpected number of parents. Expected 1, got {0}")
            print(sTxt.format(iNo_of_parents))
            return None

        dNew_area["parent"] = parent_my_id

    else:
        """ Entry of 'i_am_world' is to indicate that this is the initial
        ancestor. This sets the parent field to None"""
        dNew_area["parent"] = None

    # Obtain the reference to the CAD map. The maps available have their own
    # database entry
    cMaps = db.maps_db(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dMap_query = cMaps.find(xParam, xRestr)

    iNo_of_maps = 0
    dMap_copy = []

    for dMap in dMap_query:
        iNo_of_maps += 1
        dMap_copy.append(dMap)

# Setup a menu of the maps available
    # Setup an option of entering a region which is not mapped
    sMenu = "\n0: No map\n"
    iCnt = 0

    # Go through all the available maps.
    for one_map in dMap_copy:
        iCnt += 1
#        xScale = "{:.1e}".format(one_map["fScale"])           # 1.0e6 for 1:1M
        xScale = "{0:,}".format(int(one_map["fScale"]))    # Commas every 1000's
        sTxt = "{0}: {1}, {2} 1:{3}\n"
        sMenu += sTxt.format(iCnt, one_map["sRegion"], one_map["iYear"], xScale)
    sMenu += "x: Invalid choice will exit this sub menu"
    print(sMenu)

# Get the response from the user, with reference to the menu being offered.
    sInput = input()
    if sInput.isnumeric() == False:
        # An inbuilt 'abort' system where the user can enter 'x' to exit.
        print("\nInput is not a numeric value. Returning to menu")
        return None

    # Get the details from the dictionary and write them into the destinations
    # entry.
    iInput = int(sInput)
    if(iInput == 0):
        dNew_area["aMap"]["sRegion"] = "No Map"
        dNew_area["aMap"]["iYear"] = None
        dNew_area["aMap"]["fScale"] = None
    elif(iInput > iCnt):
        print("\nChoice out of range. Returning to menu")
        return None
    else:
        iIdx = iInput - 1
        dNew_area["aMap"]["sRegion"] = dMap_copy[iIdx]["sRegion"]
        dNew_area["aMap"]["iYear"] = dMap_copy[iIdx]["iYear"]
        dNew_area["aMap"]["fScale"] = dMap_copy[iIdx]["fScale"]

# Map location: Co-ordinates on the speciied CAD map.
    if(dNew_area["aMap"]["fScale"] != None):
        # This only works if the map exists.
        sQuestion = "\nEnter the x-coordinate from the map:"
        fX = misc.get_float(sQuestion, None, True)
        if fX == None: return None
        dNew_area["aMap"]["x"] = fX

        sQuestion = "\nEnter the y-coordinate from the map:"
        fY = misc.get_float(sQuestion, None, True)
        if fY == None: return None
        dNew_area["aMap"]["y"] = fY

        sQuestion = "\nEnter the area in mm2 from the map:"
        fA = misc.get_float(sQuestion)
        if fA == None: return None
        dNew_area["aMap"]["a"] = fA

    # Calcluate the area.
        dArea = misc.calc_area(
                dNew_area["aMap"]["a"],
                dNew_area["aMap"]["fScale"]
        )
        if dArea == None: return None
        dNew_area["aArea"] = dArea
    # End of map location entry

# TODO: Perhaps put this in the data base.
    sMenu = """
Enter the geo-political division currently being logged:
0:  World / Свьят        | *
1:  Country / Паньстфо   | 0V9                  : Trèmbovice
2:  Province / Провинцъя | V                    : Dzþevogurski,
3:  District / Повят     | VA                   : Vænesston D.
4:  County / Воевуцтво   | VAA                  : Vænesston C.
5:  Municipality / Гмина | VAA-0                : Vænesston M.
6:  Section / Чэьсть     | VAA-0M               : Miroslav
7:  Suburb / Пшэдщместе  | VAA-0MF              : Filed Tooth
8:  Street / Ульица      | VAA-0MF-A            : Archery Rd
9:  Property /Дзялка     | VAA-0MF-A01          : House number
    """
    print(sMenu)
    sInput = input()

    if sInput == "0":
        dNew_area["aType"] = {"lat":"World", "cyr":"Свьят", "lvl":"0"}
    elif sInput == "1":
        dNew_area["aType"] = {"lat":"Country", "cyr":"Паньстфо", "lvl":"1"}
    elif sInput == "2":
        dNew_area["aType"] = {"lat":"Province", "cyr":"Провинцъя", "lvl":"2"}
    elif sInput == "3":
        dNew_area["aType"] = {"lat":"District", "cyr":"Повят", "lvl":"3"}
    elif sInput == "4":
        dNew_area["aType"] = {"lat":"County", "cyr":"Воевуцтво", "lvl":"4"}
    elif sInput == "5":
        dNew_area["aType"] = {"lat":"Municipality", "cyr":"Гмина", "lvl":"5"}
    elif sInput == "6":
        dNew_area["aType"] = {"lat":"Section", "cyr":"Чэьсть", "lvl":"6"}
    elif sInput == "7":
        dNew_area["aType"] = {"lat":"Suburb", "cyr":"Пшэдщместе", "lvl":"7"}
    elif sInput == "8":
        dNew_area["aType"] = {"lat":"Street", "cyr":"Ульица", "lvl":"8"}
    elif sInput == "9":
        dNew_area["aType"] = {"lat":"Property", "cyr":"Дзялка", "lvl":"9"}
    else:
        print("Invalid selection. Returning to menu")
        return None

    sMenu = """
What is the purpose of this region:
0:  General -- No specific use, mixed description or known to have subordinates
1:  Nature -- Protected natural environment. Some infrastructure is permitted.
2:  Government -- Land reserved for development for undisclosed purpose.
3:  Military -- Area dedicated to training of the armed forces.
4:  Industrial -- Production or extraction of resources/goods/commodities.
5:  Agricultural -- Growing of food, includes animal pastures.
6:  Transport -- Logistics (Airports / train stations / water harbours).
7:  Suburb -- Residential section of a larger town.
8:  Commercial District -- Area dominated by offices.
9:  Town -- Area of balanced demand and suppy of workorce.
10: Settlement -- Small area of balanced workforce, but has limited services.
    """
    print(sMenu)
    sInput = input()

    if sInput == "0":
        dNew_area["sub_type"] = "General"
    elif sInput == "1":
        dNew_area["sub_type"] = "Nature"
    elif sInput == "2":
        dNew_area["sub_type"] = "Government"
    elif sInput == "3":
        dNew_area["sub_type"] = "Military"
    elif sInput == "4":
        dNew_area["sub_type"] = "Industrial"
    elif sInput == "5":
        dNew_area["sub_type"] = "Agricultural"
    elif sInput == "6":
        dNew_area["sub_type"] = "Transport"
    elif sInput == "7":
        dNew_area["sub_type"] = "Suburb"
    elif sInput == "8":
        dNew_area["sub_type"] = "Commercial District"
    elif sInput == "9":
        dNew_area["sub_type"] = "Town"
    elif sInput == "10":
        dNew_area["sub_type"] = "Settlement"
    else:
        print("\nInvalid selection. Returning to menu")
        return None

    bExit = False
    # The loop allows the user to edit the name. The randomly generated name
    # could be a mere suggestion, and the user may reject it and re-enter it
    # manually, adjusting the spelling.

    while bExit == False:
        sMenu = "\nDo you want a random name?"
        sRand_name_yn = misc.get_binary(sMenu)
        if sRand_name_yn == None: return None

        # User written name.
        if sRand_name_yn == "N":
            print ("\nPlease enter the name of the location in Latin. "
                    +"(Use international Keyboard)")
            dNew_area["aName"]["lat"] = input()

            # User entered name in Cyrillic
            print ("\nНапиш име обшару в Цырполю (пшэлаьч клавятурэ рэьчне)")
            dNew_area["aName"]["cyr"] = input()

        # Randomly generated name.
        elif sRand_name_yn == "Y":
            # Operated by an external routine
            import modules.x_random_names as rnd_name

            # We are storing the random names from the various systems here.
            # Hence, we will build up one set of arrays for the user to choose
            aLat, aCyr = [], []

            # 10 possible names: first three are 2-syllable
            aSyl_names = rnd_name.rnd_syllable([2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

            # Transfer the names to the common array
            for syl in aSyl_names:
                aLat.append(syl["lat"])                               # Latin
                aCyr.append(syl["cyr"])                               # Cyrillic

        # Male names
            aName = rnd_name.rnd_male_name(1)
            for name in aName:
                aLat.append(name["lat"])
                aCyr.append(name["cyr"])

        # Female names
            aName = rnd_name.rnd_female_name(1)
            for name in aName:
                aLat.append(name["lat"])
                aCyr.append(name["cyr"])

        # Static surname names
            aName = rnd_name.qRnd_static_surname(1)
            for name in aName:
                aLat.append(name["lat"])
                aCyr.append(name["cyr"])

        # Dynamic surname names
            aName = rnd_name.qRnd_dynamic_surname(1)
            for name in aName:
                aLat.append(name["lat"])
                aCyr.append(name["cyr"])

        # Male-based surnames
            aName = rnd_name.qRnd_male_surname(1)
            for name in aName:
                aLat.append(name["lat"])
                aCyr.append(name["cyr"])

        # Display the names
            iNo_of_names = len(aLat)
            sChoices = "0: Choose again\n"              # Don't like the options
            iCnt = 1
            for idx in range(0, iNo_of_names):
                sTxt = "{0}: {1} / {2}\n"
                sChoices += sTxt.format(iCnt, aLat[idx], aCyr[idx])
                iCnt += 1

            iChoice = misc.get_int(sChoices, iNo_of_names)
            if iChoice == None: return None                     # Invalid choice
            if iChoice == 0: continue                            # Choose again.
            iChoice -= 1

            dNew_area["aName"]["lat"] = aLat[iChoice]
            dNew_area["aName"]["cyr"] = aCyr[iChoice]

        else:
            print("Invalid choice. Exiting")
            return None

    # Confirm the name choice
        sNew_lat = dNew_area["aName"]["lat"]
        sNew_cyr = dNew_area["aName"]["cyr"]
        sMenu = "Are the names '{0}' / '{1}' OK?".format(sNew_lat, sNew_cyr)
        sNames_ok_yn = misc.get_binary(sMenu)
        if sNames_ok_yn == "Y": bExit = True

# GEO_CODE
# TODO: Validation
    sMenu = "\nIs the geo-code known?"
    sGeo_known = misc.get_binary(sMenu)

    if sGeo_known == "Y":
        aName = dNew_area["aName"]
        sTxt = "\nPlease enter the geocode for {0} / {1}"
        sPlace_name = sTxt.format(aName["lat"], aName["cyr"])
        print(sPlace_name)
        sGeocode = input().upper()
        dNew_area["geo_code"] = sGeocode

# Register this "child" with its "parent"
    parent = dNew_area["parent"]
    if parent == None:                       # In the case of creating a world
        cDest.insert_one(dNew_area)
        print("\n>>>\nNew area '{0}' added".format(dNew_area["aName"]["lat"]))
        return True

    xParam = {"my_id":parent}
    xRestr = {"_id":0, "aChildren":1}
    dParent_query = cDest.find(xParam, xRestr)

    for x in dParent_query:
        aChildren = x["aChildren"]
        # Add the ID of the child to the parent's list
        aChildren.append(sNew_id)

        parent = dNew_area["parent"]
        xParam = {"my_id":parent}
        # Overwrite the previous aChildren array
        xNew_data = {"$set": {"aChildren" : aChildren}}
        dParent_query = cDest.update_one(xParam, xNew_data)

        cDest.insert_one(dNew_area)

        print("\n>>>\nNew area '{0}' added".format(dNew_area["aName"]["lat"]))
        break

#-------------------------------------------------------------------------------
# 2: VIEW THE CHILDREN OF A GEOCODE
#-------------------------------------------------------------------------------
def view_children(ccTremb):
    """ Views the hierarchial children for the geo-code provided. Method outputs
    a .txt file, in the logs folder. As an example, the list counties would be
    at 'Logs/d_TJ_children.txt'"""

    sMenu = "\nEnter the geo-code for the parent (ex: V, GY, GYN...)"
    print(sMenu)
    sParent = input().upper()                # Force to upper case (consistency)

    # Access the database.
    cDest = db.destinations(ccTremb)

    xParam = {"geo_code" : sParent}
    xRestr = {"_id":0, "aChildren":1, "aName":1}
    dChild_query = cDest.find(xParam, xRestr)

    iNo_of_hits = 0
    dThe_children = None                                      # Context breaking
    aName = None
    for my_query in dChild_query:
        iNo_of_hits += 1
        dThe_children = my_query["aChildren"]     # pull the query for later use
        aName = my_query["aName"]

    # Reject if there is more that one geo-code registered
    if iNo_of_hits != 1:
        sTxt = "\n\aUnexpected number of geo-codes {0} (expecting 1)"
        print(sTxt.format(iNo_of_hits))
        return None

    # Open a text file where a copy of the information will be written to.
    if sParent == "*":
        sFile_name = "world"                    # Exception in naming convention
    else:
        sFile_name = sParent

    # Work out a name of the file
    sFile_path = "Logs/d_{0}_children.txt".format(sFile_name)
    eChild_data = open(sFile_path, "w", encoding="utf-8")

    # Write the heading of the file
    sLat_name = aName["lat"]
    sCyr_name = aName["cyr"]
    sHeading = "List of all hierarchial children for {0} ({1} / {2})\n"
    eChild_data.write(sHeading.format(sParent, sLat_name, sCyr_name))

    # Get details of the children
    sScreen = "{0}\n".format(sHeading)

    for child in dThe_children:
        xParam = {"my_id" : child}
        xRestr = {"_id":0}
        dChild_query = cDest.find(xParam, xRestr)

        # Go through every child's details
        for query in dChild_query:
        # Identifier
            sFile_data = "{0} ".format(query["my_id"])
            sScreen = "{0} ".format(query["my_id"])

        # Co-ordinates (for the file)
            sMap = query["aMap"]["sRegion"]
            fScale = query["aMap"]["fScale"]
            sX = query["aMap"]["x"]
            sY = query["aMap"]["y"]
            sA = query["aMap"]["a"]
            sScale = "%.0e" % fScale                          # convert to '4e6'
            sFile_data += "[{0}, 1:{1}] ".format(sMap, sScale)
            sFile_data += "(x:{0}; y:{1}; a:{2}) ".format(sX, sY, sA)

        # Area (for the screen)
            fQty = query["aArea"]["qty"]
            sUom = query["aArea"]["uom"]
            sScreen += " ({0}{1}) ".format(fQty, sUom)

        # Geo code
            sGeocode = query["geo_code"]
            sFile_data += "{0} ".format(sGeocode)
            sScreen += "{0} ".format(sGeocode)

        # Names
            sLat = query["aName"]["lat"]
            sCyr = query["aName"]["cyr"]
            sName = "{0} / {1}".format(sLat, sCyr)
            sFile_data += sName
            sScreen += sName

        # Output the data
            print(sScreen)
            eChild_data.write("{0}\n".format(sFile_data))
    eChild_data.close()

#-------------------------------------------------------------------------------
# 3: EXPORT DATABASE ENTRY TO FILE FOR A SINGLE GEOCODE
#-------------------------------------------------------------------------------
def view_single(ccTremb):
    """ Writes all the elements of the database to a text file"""
    sMenu = "\nEnter the geo-code for the element sought (ex: V, GY, GYN...)"
    print(sMenu)
    sGeo_code = input().upper()              # Force to upper case (consistency)

    # Access the database.
    cDest = db.destinations(ccTremb)

    xParam = {"geo_code" : sGeo_code}
    xRestr = {"_id":0}
    dQuery = cDest.find(xParam, xRestr)

    # Pull data and veryify existance
    iNo_of_hits = 0
    dData = ""

    for query in dQuery:
        dData = query
        iNo_of_hits += 1

    # Make sure that only one entry exists
    if iNo_of_hits != 1:
        sTxt = ("\n\aThere were {0} 'hits' while expecting 1 for [{1}]")
        print(sTxt.format(iNo_of_hits, sGeo_code))
        return None

    # Open a text file where a copy of the information will be written to.
    if sGeo_code == "*":
        sFile_name = "world"                    # Exception in naming convention
    else:
        sFile_name = sGeo_code

    # Work out a name of the file
    sFile_path = "Logs/d_{0}_single.txt".format(sFile_name)
    eSingle_data = open(sFile_path, "w", encoding="utf-8")

    eSingle_data.write("{0}\n".format(dData))
    eSingle_data.close()

    print("Please see: {0}".format(sFile_path))

#-------------------------------------------------------------------------------
# 4: PRETTY-PRINT MANUALLY DATABASE ENTRY TO FILE FOR A SINGLE GEOCODE
#-------------------------------------------------------------------------------
def pretty_print_single(ccTremb):
    """ Writes most of the elements from the database in a human-readable format
    """
    import datetime

    sMenu = "\nEnter the geo-code for the element sought (ex: V, GY, GYN...)"
    print(sMenu)
    sGeo_code = input().upper()              # Force to upper case (consistency)

# Access the database.
    cDest = db.destinations(ccTremb)

    xParam = {"geo_code" : sGeo_code}
    xRestr = {"_id":0}
    dQuery = cDest.find(xParam, xRestr)

    # Obtain the data
    dData = ""
    for query in dQuery:
        dData = query

    # Check that we have data
    if dData == "":
        print("\n\aNo information available. Check your geo-code")
        return None

# Open a text file where a copy of the information will be written to.
    if sGeo_code == "*":
        sFile_name = "world"                    # Exception in naming convention
    else:
        sFile_name = sGeo_code

# Work out a name of the file
    sFile_path = "Logs/d_{0}_pretty.txt".format(sFile_name)
    eSingle_data = open(sFile_path, "w", encoding="utf-8")

# Write the title
    xNow = datetime.datetime.now()

    sTxt =  "    {0} {1} / {2} {3}\n"
    sTxt += "----------\n"
    sName_lat = dData["aName"]["lat"]
    sType_lat = dData["aType"]["lat"]
    sName_cyr = dData["aName"]["cyr"]
    sType_cyr = dData["aType"]["cyr"]
    sAll = sTxt.format(sName_lat, sType_lat, sType_cyr, sName_cyr)

    sTxt = "Pretty print information was generated on {0}\n".format(xNow)
    sAll += sTxt

# Identifiation information
    sAll += "----------\n"
    sAll += "my_id: {0}\n".format(dData["my_id"])
    sAll += "geo_code: {0}\n".format(dData["geo_code"])

# Shortcuts: See what information is available
    bDemogfx = dData["aDemographics"] != {}              # Short cut to boolean
    bVehicles = dData["aVehicles"] != {}
    bFootprint = dData["aFootprint"] != {}
    bWarehouse = dData["aWarehouse"] != {}

    # There is a flag set to indicate that not all the children have full data
    bInc_data = True
    sTxt_inc_data = " (Incomplete data)"
    if bDemogfx and dData["aDemographics"]["misc"] != "Incomplete Data":
        bInc_data = False
        sTxt_inc_data = ""

# TOTAL POPULATION
    sAll += "----------\n"
    if bDemogfx:
        iTot_pax = dData["aDemographics"]["iTOT-PAX"]
        sTot_pax = "{0:,}{1}".format(iTot_pax, sTxt_inc_data) # {0:,}: 23,000
    else:
        sTot_pax = "N/A"
    sAll += "Total population: {0}\n".format(sTot_pax)

# TOTAL VEHICLES
    if bVehicles:   # We have vehicle data
        iTot_veh = dData["aVehicles"]["tot_road"]
        sTot_veh = "{0:,}{1}".format(iTot_veh, sTxt_inc_data) # {0:,}: 23,000
    else:
        sTot_veh = "N/A"
    sAll += "\nTotal vehicles*: {0}\n".format(sTot_veh)
    sAll += "   *: Vehicles with a county-level (not government) number plate\n"

# WAREHOUSE CONTENTS
    if bWarehouse:
        sWhs = ""
        for sShelf in dData["aWarehouse"]:
            dItems = dData["aWarehouse"][sShelf]
            sRes = dItems["resource"]
            sQty = dItems["annual_output"]
            sUom = dItems["units"]
            sTxt = ">   {0}: {1:,}{2} by {3}\n"
            sWhs += sTxt.format(sRes, sQty, sUom, sShelf)
    else:
        sWhs = ">   N/A\n"
    sAll += "\nGoods produced{1}:\n{0}".format(sWhs, sTxt_inc_data)

# PARENT
    sAll += "----------\n"

    sParent_id = dData["parent"]
    sParent_geo = ""
    aParent_names = {}
    xParam = {"my_id" : dData["parent"]}
    xRestr = {"_id":0, "geo_code":1, "aName":1, "aType":1}
    dQuery = cDest.find(xParam, xRestr)
    for dItems in dQuery:
        sParent_geo = dItems["geo_code"]
        aParent_names = dItems["aName"]
        aParent_type = dItems["aType"]

    sTxt =  "Hierarchial Parent: \n"
    if sParent_id != None:
        sTxt += ">  {0} {1} / {2} {3}\n".format(
            aParent_names["lat"], aParent_type["lat"],
            aParent_type["cyr"], aParent_names["cyr"])
        sTxt += ">   my_id: {0}\n".format(sParent_id)
        sTxt += ">   geo_code: {0}\n".format(sParent_geo)
    else:
        sTxt += ">   No parent declared\n"
    sAll += sTxt

# CHILDREN:
    sAll += "----------\n"
    sAll += "Hierarchial Children: \n"
    iNo_of_children = len(dData["aChildren"])
    sAll += ">   count: {0}\n".format(iNo_of_children)

    # Go through every child
    for sChd_id in dData["aChildren"]:
        sChd_geo = ""
        aChd_names = {}
        aChd_type = {}
        aChd_dgfx = {}
        aChd_whs = {}
        xParam = {"my_id" : sChd_id}
        xRestr = {"_id":0, "geo_code":1, "aName":1,
                  "aType":1, "aDemographics":1, "aWarehouse":1}
        dQuery = cDest.find(xParam, xRestr)

    # Pull data from the query
        for dItems in dQuery:
            sChd_geo = dItems["geo_code"]
            aChd_names = dItems["aName"]
            aChd_type = dItems["aType"]
            aChd_dgfx = dItems["aDemographics"]
            aChd_whs = dItems["aWarehouse"]

    # Do the population count
        if aChd_dgfx != {}:
            sDgfx = "{0:,}".format(aChd_dgfx["iTOT-PAX"])
            if aChd_dgfx["misc"] == "Incomplete Data":
                sDgfx += " (Incomplete data)"
        else:
            sDgfx = "N/A"

    # Get the child's warehouse in order.
        sWhs = ""   # Build up child's warehouse list
        for sStore in aChd_whs:
            sWhs += "{0}, ".format(aChd_whs[sStore]['resource'])
        sWhs = sWhs[:-2]        # Drop the final space and comma

    # Present the information
        sTxt =  ">      {0} {1} / {2} {3}\n".format(
            aChd_names["lat"], aChd_type["lat"],
            aChd_type["cyr"], aChd_names["cyr"])
        sTxt += ">          my_id: {0}\n".format(sChd_id)
        sTxt += ">          geo_code: {0}\n".format(sChd_geo)
        sTxt += ">          population: {0}\n".format(sDgfx)
        sTxt += ">          warehouse: {0}\n".format(sWhs)
        sTxt += ">\n"        # For readibility
        sAll += sTxt

# MAP:
    sAll += "----------\n"
    sAll += "Map and area: \n"
    aMap = dData["aMap"]
    if aMap["sRegion"] != "No Map":
        iScale = int(aMap["fScale"])
        sTxt = ">   Region: {0} 1:{1:,} (drawn in {2})\n"
        sAll += sTxt.format(aMap["sRegion"], iScale, aMap["iYear"])

        sTxt = ">   Position (mm) x: {0}, y: {1}\n"
        sAll += sTxt.format(aMap["x"], aMap["y"])

        sTxt = ">   Area on paper (sq.mm) a: {0:,}\n"
        sAll += sTxt.format(aMap["a"])

        aArea = dData["aArea"]
        sTxt = ">   Area represented: {0:,}{1}\n"
        sAll += sTxt.format(aArea["qty"], aArea["uom"])

    else:
        sAll +=  ">   No map declared\n"

# DEMAND FOR WORKFORCE:
    sAll += "----------\n"
    sAll += "Workforce Demand: \n"
    dDmd_wkf = dData["aDemand_workforce"]

    # Obtain the total
    iTot_wkf = 0                        # Count them up for conveniance
    for sGroup in dDmd_wkf["total"]:
        if sGroup == "iVeh_cnt": continue       # Not population.
        iTot_wkf += dDmd_wkf["total"][sGroup]

    sTxt = ">   Grand Total: ({0:,})\n>      ".format(iTot_wkf)

    # Do the men on the top line
    for sGroup in ["rm", "hm", "mm", "lm", "pm"]:
        sTxt += " {0}: {1:,};".format(sGroup, dDmd_wkf["total"][sGroup])
    sTxt += "\n>      "

    # Do the women on the bottom line
    for sGroup in ["rf",  "hf", "mf", "lf", "pf"]:
        sTxt += " {0}: {1:,};".format(sGroup, dDmd_wkf["total"][sGroup])
    sTxt += "\n>\n"
    sAll += sTxt

    # ITEMISED:
    aItemised = dDmd_wkf["aItemised"]
    for dItem in aItemised:
        # Get the total for the itemised item.
        iItem_tot = 0                                 # Add up for conveniance
        for sGroup in dItem:
            if sGroup in ["sCode", "sName", "iVeh_cnt"]:   # "or" the cheap way
                continue
            iItem_tot += dItem[sGroup]

        # Hew setup vs old.
        if "sCode" in dItem.keys():
            sTxt = ">   [{2}] {0}: ({1:,})\n>      "
            sTxt = sTxt.format(dItem['sName'], iItem_tot, dItem['sCode'])
        else:
            sTxt = ">   {0}: ({1:,})\n>      "
            sTxt = sTxt.format(dItem['sName'], iItem_tot)

        # Do the men on the top line
        for sGroup in ["rm", "hm", "mm", "lm", "pm"]:
            sTxt += " {0}: {1:,};".format(sGroup, dItem[sGroup])
        sTxt += "\n>      "

        # Do the women on the bottom line
        for sGroup in ["rf",  "hf", "mf", "lf", "pf"]:
            sTxt += " {0}: {1:,};".format(sGroup, dItem[sGroup])
        sTxt += "\n>      "

        # Sometimes company vehicles (both Y and county registrations) are
        # recorded
        if "iVeh_cnt" in dItem.keys():
            sTxt += " tot road veh: {0:,}\n".format(dItem["iVeh_cnt"])
        sTxt += ">\n"
        sAll += sTxt

# WORKPLACE SUPPLIES:
    sAll += "----------\n"
    sAll += "Supply workplaces: \n"
    if "aSupply_workplace" in dData.keys():
        dSup_wkp = dData["aSupply_workplace"]
        for dItem in dSup_wkp:
            iCnt = dItem["iCnt"]
            sName = dItem["sName"]
            sCode = dItem["sCode"]
            sTxt = ">   [{2}] {0}x '{1}' used by:\n"
            sTxt = sTxt.format(iCnt, sName, sCode)
            sAll += sTxt

            # Who does this facility service?
            lServices = dItem["lServices"]
            iSvc_cnt = len(lServices)
            iSvc_idx = 0                        # Pointer
            while iSvc_idx < iSvc_cnt:          # For multiple rows
                sTxt = ">      "
                for x in range(5):
                    if iSvc_idx >= iSvc_cnt: break
                    sTxt += " {0},".format(lServices[iSvc_idx])
                    iSvc_idx += 1
                sAll += sTxt + "\n"

            # Capacity
            sAll += ">       Capacity used: {0}\n".format(dItem["fCapacity"])
    else:
        sAll += ">   N/A\n"

# DEMAND FOR HOUSEHOLDS:
    sAll += "----------\n"
    sAll += "Demand households: \n"
    dDmd_hhd = dData["aDemand_hholds"]

    # Check which 'version' of data this is.
    if "total" in dDmd_hhd.keys():
        # Calculate the total of the housing demand across all groups
        iTot_dmd_hhd = 0
        for sGroup in dDmd_hhd["total"]:
            iTot_dmd_hhd += dDmd_hhd["total"][sGroup]
        sTxt = ">   Grand Total: ({0:,})\n>      ".format(iTot_dmd_hhd)

        # Process the groups within the total
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDmd_hhd["total"][sGroup])
        sTxt += "\n"
        sAll += sTxt

        # DO THE ITEMS:
        aItemised = dDmd_hhd["aItemised"]
        for dItem in aItemised:
            iTot_dmd_item = 0
            for sGroup in dItem:
                if sGroup == "sName": continue
                iTot_dmd_item += dItem[sGroup]

            # Write the text.
            sTxt =  ">   {0}: ({1:,}) |".format(dItem["sName"], iTot_dmd_item)

            # Process the groups within the total
            for sGroup in ["r", "h", "m", "l", "p"]:
                sTxt += " {0}: {1:,};".format(sGroup, dItem[sGroup])
            sTxt += "\n"
            sAll += sTxt

    # NON-ITEMISED GROUP: Here, the demand was calculated directly.
    else:
        # Calculate the total of the housing demand across all groups
        iTot_dmd_hhd = 0
        for sGroup in dDmd_hhd:
            iTot_dmd_hhd += dDmd_hhd[sGroup]
        sTxt = ">   Totals: ({0:,}) | ".format(iTot_dmd_hhd)

        # Process the groups within the total
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDmd_hhd[sGroup])
        sTxt += "\n"
        sAll += sTxt

# SUPPLY HOUSEHOLDS:
    sAll += "----------\n"
    sAll += "Supply households: \n"
    dSup_hhd = dData["aSupply_hholds"]

    # Calculate the total of the housing demand across all groups
    iTot_sup_hhd = 0
    for sGroup in dSup_hhd["total"]:
        iTot_sup_hhd += dSup_hhd["total"][sGroup]
    sTxt = ">   Grand Total: ({0:,})\n>      ".format(iTot_sup_hhd)

    # Process the groups within the total
    for sGroup in ["r", "h", "m", "l", "p"]:
        sTxt += " {0}: {1:,};".format(sGroup, dSup_hhd["total"][sGroup])
    sTxt += "\n"
    sAll += sTxt

    # DO THE ITEMS:
    aItemised = dSup_hhd["aItemised"]
    for dItem in aItemised:
        iTot_sup_item = 0
        for sGroup in dItem:
            if sGroup == "sName": continue
            iTot_sup_item += dItem[sGroup]

        # Write the text.
        sTxt =  ">   {0}: ({1:,}) |".format(dItem["sName"], iTot_sup_item)

        # Process the groups within the total
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dItem[sGroup])
        sTxt += "\n"
        sAll += sTxt

# DEMOGRAPHICS
    sAll += "----------\n"
    sAll += "Demographics:\n"
    dDfx = dData["aDemographics"]       # Short-cut
    if dDfx != {}:
        sTxt = ">   TOTAL PEOPLE: {0:,}\n>\n"
        sAll += sTxt.format(dDfx["iTOT-PAX"])

        sTxt = ">   Married working people (aHHM-PAX):\n>      "
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aHHM-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Married retired people (aHHR-PAX):\n>      "
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aHHR-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Unmarried working people ('bachelors') (aHHB-PAX):\n>      "
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aHHB-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Unmarried retired people ('golden oldies') (aHHO-PAX):"
        sTxt += "\n>      "                 # We exceeded the 80 column limit
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aHHO-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Disabled people, not in a nursing home (aHHD-PAX):\n>      "
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aHHD-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Not working: housewife/-husband OR disabled caregiving "
        sTxt += "(aHHX-PAX):\n>      "
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aHHX-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Unemployed: wanting to work but no work available "
        sTxt += "(aUNE-PAX):\n>      "
        for sGroup in ["r", "h", "m", "l", "p"]:
            sTxt += " {0}: {1:,};".format(sGroup, dDfx["aUNE-PAX"][sGroup])
        sTxt += "\n>\n"
        sAll += sTxt

        sTxt = ">   Preschoolers, all groups                 (ED0-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED0-PAX"])

        sTxt = ">   Primary schoolers, all groups            (ED1-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED1-PAX"])

        sTxt = ">   Middle schoolers, all groups             (ED2-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED2-PAX"])

        sTxt = ">   High schoolers, all groups               (ED3-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED3-PAX"])

        sTxt = ">   Religious or Private schoolers, all grps (ED4-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED4-PAX"])

        sTxt = ">   College students, all groups             (ED5-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED5-PAX"])

        sTxt = ">   Polytechnic students, all groups         (ED6-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED6-PAX"])

        sTxt = ">   University students, all groups          (ED7-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED7-PAX"])

        sTxt = ">   --- (empty slot), all groups             (ED8-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED8-PAX"])

        sTxt = ">   Disabled students, all groups            (ED9-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED9-PAX"])

        sTxt = ">   Nursing home for the rich, group 'r'     (OAR-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["OAR-PAX"])

        sTxt = ">   Old Age Home, all groups                 (OAH-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["OAH-PAX"])

        sTxt = ">   Private nurse, all groups                (OAN-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["OAN-PAX"])

        sTxt = ">   Youth prison, all groups                 (YXJ-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["YXJ-PAX"])

        sTxt = ">   Adult prison, all groups                 (YXA-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["YXA-PAX"])

        # RELIGION:
        cDemogfx_const = db.demogfx_const(ccTremb)
        xParam = {}
        xRestr = {"_id":0}
        dDb = cDemogfx_const.find(xParam, xRestr)

        # Get the names and the codes from the database
        dFull_db = {}
        for dQuery in dDb:
            for xKey, xVal in dQuery.items():
                dFull_db[xKey] = xVal    # Copy out the data

        # Extract the religions
        adReligion = dFull_db["aaReligion"]
        sAll += ">   Religion:\n"
        for dRel in adReligion:
            sCode = dRel["code"]
            sTxt = ">      {0} ({1}): {2}\n"
            sAll += sTxt.format(dRel["adj"], sCode, dDfx["aREL-PAX"][sCode])

        sTxt = ">   Potential public transport users         (BUS-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["BUS-PAX"])

        sTxt = ">   Vehicle, bicycle                         (VEH-BIC): {0:,}\n"
        sAll += sTxt.format(dDfx["VEH-BIC"])

        sTxt = ">   Vehicle, motorbike*                      (VEH-MBK): {0:,}\n"
        sAll += sTxt.format(dDfx["VEH-MBK"])

        sTxt = ">   Vehicle, car*                            (VEH-CAR): {0:,}\n"
        sAll += sTxt.format(dDfx["VEH-CAR"])

        sTxt = ">   Vehicle, aircraft**                      (VEH-AIR): {0:,}\n"
        sAll += sTxt.format(dDfx["VEH-AIR"])

        sAll += ">    * = Requires county-level 'number plates' "
        sAll += "(ex: 'GYN-00342')\n"
        sAll += ">   ** = Requires federal-level 'call sign'    "
        sAll += "(ex:  'V9-AGB')\n"
    else:
        sAll += ">   N/A\n"

# VEHICLES REQUIRING COUNTY-LEVEL REGISTRATION AND NUMBER-PLATE RENTAL
    sAll += "----------\n"
    sAll += "Vehicles (requiring county-level registration and"
    sAll += " number plates):\n"
    dVeh = dData["aVehicles"]       # Short-cut
    if dVeh != {}:
        sTxt = ">   TOTAL ROAD: {0:,}\n"
        sAll += sTxt.format(dVeh["tot_road"])   # Leave room for aircraft

        # Itemise the road vehicles
        aItemised = dVeh["aItemised"]
        sAll += ">   Itemised county-registered vehicles:\n"
        for sItem in aItemised:
            sTxt = ">      {0}: {1:,}\n"
            sAll += sTxt.format(sItem, aItemised[sItem])
    # TODO: AIRCRAFT
    else:
        sAll += ">   N/A\n"

# FOOTPRINT
    sAll += "----------\n"
    sAll += "Footprint on the land:\n"
    dFp = dData["aFootprint"]       # Short-cut
    if dFp != {}:
        # Publish if it exists
        for sItem in dFp:
            if "val" in dFp[sItem].keys():
                fVal = dFp[sItem]["val"]
            else:
                fVal = dFp[sItem]["qty"]
            units = dFp[sItem]["uom"]
            sTxt = ">   {0}: {1:,}{2}\n"
            sAll += sTxt.format(sItem, fVal, units)
    else:
        sAll += ">   N/A\n"

# Write to the file
    print("Please see: {0}".format(sFile_path))
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()


#-------------------------------------------------------------------------------
# B: BALANCE A TOWN
#-------------------------------------------------------------------------------
def balance_town(ccTremb):
    """ Picks up the geo-code from the prompt. It then assigns the basic
    services:
        (5YP) police,
        (5YF) fire,
        (5YH) community clinic,
        (5YG) community governance,
        (ED0) community pre-school,
        (ED1) community primary school,
        (ED2) community middle school,
        (ED3) community high school,
        (OAH) old age home,
        (5SŠ) small shop (the corner grocer),
        (5LX) community library,
        (5TH) community theatre,
        (5PO) community post office,
    ... using a subroutine. Once they are in, then a 5-iteration loop is entered
    where the total population is recalculated. As the population increases,
    the Population-dependant services are adjusted accordingly
        """

    sTxt = ("\nPlease enter the geo-code ('GYN-G' for example) of the area" +
    " you wish to balance")
    print(sTxt)
    sGeo_code = input().upper()

# Build the first demographic
    sOut = qHhold_demands(ccTremb, sGeo_code)
    if sOut == None:
        return None

# Loop of iterations
    for iCnt in range(5):
        sOut = qServices_demands(ccTremb, sGeo_code)    # Adds the demand
        if sOut == None:
            return None     # Error was found
        sOut = qHhold_demands(ccTremb, sGeo_code)
        if sOut == None:
            return None
    print("\nBalancing complete")
    return True


#-------------------------------------------------------------------------------
# E: EDIT AN ENTRY
#--------------------------------------------------------------------------------
def edit_entry(ccTremb):
    """ Accepts 'my_id' identifier and retrieves that record. It then outputs
    all the details of it on the screen and in the file. The user will then have
    an opportunity to edit any element or sub-element"""

    print("Enter the 'my_id' identifier you wish to edit")
    sEdit_my_id = input().upper()           # Allows the user to enter lowercase

    # Access the database.
    cDest = db.destinations(ccTremb)
    xParam = {"my_id" : sEdit_my_id}
    xRestr = {"_id":0}
    dId_query = cDest.find(xParam, xRestr)

    # show what we harvested
    iCnt = 0
    for query in dId_query:
        iCnt += 1
        print("{0}".format(query))

    # Verify that we have data
    if iCnt != 1:
        print("Item {0} not found or has been duplicated".format(sEdit_my_id))
        return None

    # As what we want to modify.
    print("\nEnter the key of the value you wish to modify. "
    +"Hint: use a dot to enter an array, for example 'aMap.a'")
    sKey_of_mod = input()

    xParam = {"my_id" : sEdit_my_id}
    xRestr = {"_id":0, sKey_of_mod:1}
    dId_query = cDest.find(xParam, xRestr)
    for query in dId_query:
        print("Current value(s) is/are:\n{0}".format(query))

    sMenu = """
Select expected data type:
1:  Float (number with decimal point)
2:  String (Latin / Cyrillic / alphanumeric codes)
3:  TODO: Array-String Add.
4:  Array-String Remove.
5:  Delete the item by assigning a 'None'
"""
    print(sMenu)
    sChoice = input()
    xNew_value = None

    print("\nEnter the value to update with:")
    sNew_value = input()

    if sChoice == "1":      # float
        try:
            xNew_value = float(sNew_value)
        except:
            print("Can't convert '{0}' to float".format(sNew_value))
            return None

    elif sChoice == "2":    # String, so do nothing
        xNew_value = sNew_value

    elif sChoice == "4":
        # The query dereferences itself after being read.
        # Hence, a new query is needed.
        xParam = {"my_id" : sEdit_my_id}
        xRestr = {"_id":0, sKey_of_mod:1}
        dId_query = cDest.find(xParam, xRestr)
        for query in dId_query:
            for aThe_array in query.values():
                try:
                    aThe_array.remove(sNew_value)
                except:
                    sTxt = "Unable to remove '{0}' from the list"
                    print(sTxt.format(sNew_value))
                    return None
            xNew_value = aThe_array

    elif sChoice == "5":
        xNew_value = None

    xParam = {"my_id" : sEdit_my_id}
    xNew_data = {"$set": {sKey_of_mod : xNew_value}}
    dParent_query = cDest.update_one(xParam, xNew_data)

    xParam = {"my_id" : sEdit_my_id}
    xRestr = {"_id":0, sKey_of_mod:1}
    dId_query = cDest.find(xParam, xRestr)
    for query in dId_query:
        print("after the modification:\n{0}".format(query))

#-------------------------------------------------------------------------------
# G: ADD GEOCODE TO A NEWLY CREATED AREA
#-------------------------------------------------------------------------------
def assign_geocodes(ccTremb):
    """ Takes in the parent's geocode. Method then determines which children
    need to be assigned their own geocodes. Both manual and automatic methods
    are available"""

    print("\nEnter the geocode of the parent (TJ for example)"
          +" of the children witout geocodes")
    sParent = input().upper()

    # Access the database.
    cDest = db.destinations(ccTremb)

    xParam = {"geo_code" : sParent}
    xRestr = {"_id":0, "aChildren":1, "aName":1}
    dChild_query = cDest.find(xParam, xRestr)

# EXTRACT THE DATA FROM THE DATABASE
    iNo_of_hits = 0
    aThe_children = None                                      # Context breaking
    aName = None                                              # Context breaking
    for my_query in dChild_query:
        iNo_of_hits += 1
        aThe_children = my_query["aChildren"]
        aName = my_query["aName"]

    # Reject if there is more that one geo-code registered
    if iNo_of_hits != 1:
        sTxt = "Unexpected number of geo-codes {0} (expecting 1)"
        print(sTxt.format(iNo_of_hits))
        return None

    # Reject if no children are found
    iNo_of_children = len(aThe_children)
    if iNo_of_children == 0:
        print("There are no children for this parent. Exiting")
        return None

    if iNo_of_children > 36:
        print("There are too many 'children' move some"
              + " of them to another parent")
        return None

# PREPARE THE LIST OF POSSIBLE GEOCODES
    sGeo_string = "ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789O"   # Note 'oscar' (last)
    aGeo_avail = []

    # convert the string to array
    for s in sGeo_string:
        aGeo_avail.append(s)

# loop through in case of manual or a semi-automatic process.
    bExit = False
#   while bExit == False
    aChildren = []

# Query the children individually
    for sChild_id in aThe_children:
        xParam = {"my_id" : sChild_id}
        xRestr = {"_id":0, "geo_code":1, "aName":1, "my_id":1}
        dQuery = cDest.find(xParam, xRestr)

        for x in dQuery:
            dChild = {
                "my_id": x["my_id"],
                "lat": x["aName"]["lat"],
                "cyr": x["aName"]["cyr"],
                "geo": x["geo_code"]
            }
            aChildren.append(dChild)

# PROCESS THE CHILDREN
    aCodeless = []

    for aChild in aChildren:
        # Check if the child has a code assigned
        sChild_geo = aChild["geo"]
        if sChild_geo != None:
            sLast = sChild_geo[-1]
            aGeo_avail.remove(sLast)
        else:
            aCodeless.append(aChild)

    if len(aCodeless) == 0:
        print("All the children have codes already. No need to assign")
        return None

# OFFER MANUAL METHOD OF ASSIGNMENT
    sMenu = ("Do you want to begin with manual method? "
           +"(For instance the capital)")
    sYorN_manual = misc.get_binary(sMenu)
    if sYorN_manual == "Y":
        bMan_exit = False
        while bMan_exit == False:
        # Prepare the menu for the item of interest
            iChoice = 1
            sMenu = "Select the item to assign a manual code to:\n"
            for aChild in aCodeless:
                # Build up a list to display of codes that are alreay assigned
                sTxt = "{0}. ({1})  {2}\n"
                sMenu += sTxt.format(iChoice, aChild["geo"], aChild["lat"])
                iChoice += 1

        # Obtain the users choice and disqualify an invalid choice
            iChild = misc.get_int(sMenu, iChoice-1)
            if iChild == 0:
                print("Zero is an invalid choice. Please try again")
                continue
            aChild = aCodeless[iChild-1]

        # Prepare the menu for the available code extensions.
            iAvail = 1
            sMenu = "Select the available code for {0} / {1}:\n"
            sMenu = sMenu.format(aChild["lat"], aChild["cyr"])
            sBase = sParent
            if len(sBase) == 3 or len(sBase) == 7:
                sBase += "-"
            aNew_code = []
            for sCode in aGeo_avail:
                sNew_code = sBase + sCode
                aNew_code.append(sNew_code)
                sMenu += "{0}. {1}\n".format(iAvail, sNew_code)
                iAvail += 1

        # Present the choices to the user
            iCode = misc.get_int(sMenu, iAvail-1)
            if iCode == 0:
                print("Zero is an invalid choice. Please try again")
                continue
            sNew_geocode = aNew_code[iCode-1]

        # Update the data base with the choice
            xParam = {"my_id" : aChild["my_id"]}
            xNew_data = {"$set": {"geo_code" : sNew_geocode}}
            dParent_query = cDest.update_one(xParam, xNew_data)

            # Remove from the list of unassigned codes
            del(aGeo_avail[iCode-1])
            del(aCodeless[iChild-1])

            sMenu = "Any more manual assignments?"
            sYorN_more_man = misc.get_binary(sMenu)
            if sYorN_more_man != "Y":
                bMan_exit = True
        # end of Manual loop
    # end of manual choice

# AUTOMATIC ASSIGNMENTS
    iLen_of_codeless = len(aCodeless)
    if iLen_of_codeless == 0:
        print("All the items have been code-assigned. Returning")
        return None

    # See what codes are still available
    iLen_of_avail_all = len(aGeo_avail)
    iLen_of_avail_num = 0
    bOscar = False
    for x in aGeo_avail:
        if x.isnumeric() == True: iLen_of_avail_num += 1
        if x == "O": bOscar = True

    # Calculate the number of alphabetic codes left
    iLen_of_avail_alpha = iLen_of_avail_all - iLen_of_avail_num
    if bOscar == True: iLen_of_avail_alpha -= 1

    # See if we can only use the alphabetic characters
    iRange = 0
    if iLen_of_codeless <= iLen_of_avail_alpha:
        iRange = iLen_of_avail_alpha
    elif iLen_of_codeless < iLen_of_avail_all:
        iRange = iLen_of_avail_all - 1
    elif iLen_of_codeless == iLen_of_avail_all:
        iRange = iLen_of_avail_all
    else:
        print("Insufficient characters for automatic assignment")
        return None

    # Fire-up the random module
    import random

    sTxt = ("There are still {0} codes to be assigned. "
           +"Assigning them automatically")
    print(sTxt.format(iLen_of_codeless))
    for aChild in aCodeless:
    # Prepare the code
        sBase = sParent
        if len(sBase) == 3 or len(sBase) == 7:
            sBase += "-"

    # Randomise the code to be assigned
        rnd = random.randrange(0, iRange)
        sNew_geocode = sBase + aGeo_avail[rnd]
        del aGeo_avail[rnd]
        iRange -= 1

    # Save it to the database
        xParam = {"my_id" : aChild["my_id"]}
        xNew_data = {"$set": {"geo_code" : sNew_geocode}}
        dParent_query = cDest.update_one(xParam, xNew_data)

    # End of going through each child.
    print ("Geo-code assignment completed")

#-------------------------------------------------------------------------------
# H: ADD DEMAND FOR HOUSEHOLDS AND WORK OUT THE DEMOGRAPHICS
#-------------------------------------------------------------------------------
def qThe_hhold_demands(dDataIn):
    """ Method adds spouces and children to the demands. Also places people in
    nursing homes and jails. Returns 'dService_demands'"""
    import random

    # Unpack the suitcase
    dDfx = dDataIn["dDfx"]
    dService_demands = dDataIn["dService_demands"]
    sIncome = dDataIn["sIncome"]

    bHousewife = False
    # Shorten some of the demographics.
    fPartners = dDfx["aPartners"][sIncome]
    fHousewife = dDfx["aHousewife"][sIncome]
    fDisabled = dDfx["aDisabled_school"][sIncome]
    iChild_cnt = dDfx["aChildren"][sIncome]
    fCollege = dDfx["aCollege"][sIncome]
    fPolytech = dDfx["aPolytech"][sIncome]
    fUniversity = dDfx["aUniversity"][sIncome]
    fPvt_school = dDfx["aSpeciality_school"][sIncome]
    fPreschool = dDfx["preschool_rate"]
    fPrison = dDfx["prison_rate"]
    fNursing_home = dDfx["nursing_home_rate"]

    # Flag the wife as not woriking
    dService_demands["misc"] = "spouse not working"
    # Presence of a wife
    fRnd = random.random()          # Returns a float between 0 and <1.0
    if fRnd > fPartners:
       # Not married
       dService_demands["aHHB-PAX"][sIncome] += 1          # Single Male
       return dService_demands              # Single people don't have children

# MARRIED MAN
    dService_demands["aHHM-PAX"][sIncome] += 2      # Married household

        # If there is a disabled child in the household, the wife needs
        # to stay at home
    bDisabled_child = False

    # non-working children living with parents. The complexity of single
    # parents are not taken into account. This could be a TODO.

    for y in range(iChild_cnt):
        # Hazard a guess of the child's age. The calculation below is
        # means 65 - 18 = 47. The parents are in the range of 18 to 65.
        # This means that the child could be between 0 and 47 years old.
        # The '+2' allows for a scenario where the family did not make
        # a child yet.
        iAge_range = dDfx["max_work_age"] - dDfx["high_max_age"] + 2
        iRnd_age = random.randrange(iAge_range)
        iRnd_age -= 2               # compensation for childlessness

        # Child's Disability
        fRnd = random.random()
        if fRnd < fDisabled:
            bDisabled_child = True

        # Child's age:
        bInfant = False
        bToddler = False
        bPrimary = False
        bMiddle = False
        bHigh = False
        bTertiary = False

        if iRnd_age < 0:
            continue            # Childless scenario
        elif iRnd_age <= dDfx["infant_max_age"]:
            bInfant = True
            fPrison *= 0.00           # Adjust chance of prison with age
        elif iRnd_age <= dDfx["toddler_max_age"]:
            bToddler = True
            fPrison *= 0.00           # Adjust chance of prison with age
        elif iRnd_age <= dDfx["primary_max_age"]:
            bPrimary = True
            fPrison *= 0.33           # Adjust chance of prison with age
        elif iRnd_age <= dDfx["middle_max_age"]:
            bMiddle = True
            fPrison *= 0.66           # Adjust chance of prison with age
        elif iRnd_age <= dDfx["high_max_age"]:
            bHigh = True
            fPrison *= 1.00           # Adjust chance of prison with age
        elif iRnd_age <= dDfx["tertiary_max_age"]:
            bTertiary = True
            fPrison *= 1.00           # Adjust chance of prison with age
        else:
            pass

        # Tertiary education
        bCollege = False
        bPolytech = False
        bUniversity = False

        if  bTertiary:
        # Between 18 and 25
            # College chances of the child
            fRnd = random.random()
            if fRnd < fCollege:
                bCollege = True

            # College chances of the child
            fRnd = random.random()
            if fRnd < fPolytech:
                bPolytech = True

            # College chances of the child
            fRnd = random.random()
            if fRnd < fUniversity:
                bUniversity = True

    # PLAY WITH THE LOGIC
    # criminal child
        fRnd = random.random()
        if fRnd < fPrison:
            # The child is a criminal!
            if bInfant or bToddler or bPrimary or bMiddle or bHigh:
                # Remove child from school
                bInfant = False
                bToddler = False
                bPrimary = False
                bMiddle = False
                bHigh = False
                dService_demands["YXJ-PAX"] += 1    #Juvenile prison
            else:
                # Remove child from additional schooling
                bCollege = False
                bPolytech = False
                bUniversity = False
                dService_demands["YXA-PAX"] += 1    # Adult prison
            # end of prison selection
        # end of going to prison

    # The disabled child
        bSchool = bToddler or bPrimary or bMiddle or bHigh
        if bSchool and bDisabled_child:
            # Remove child from normal school
            bToddler = False
            bPrimary = False
            bMiddle = False
            bHigh = False
            dService_demands["ED9-PAX"] += 1

        if (bTertiary or bSchool) and bDisabled_child:
            # Child is less than 25 years old and disabled, hence stays
            # with parent. However, the tertiary level students can
            # study further.
            if sIncome == "r":
                dService_demands["OAN-PAX"] += 1
            else:
                bHousewife = True
                dService_demands["aHHX-PAX"][sIncome] += 1  # Caregiver

        if bTertiary and bDisabled_child:
            dService_demands["aHHD-PAX"][sIncome] += 1 # Unempl. disabl. child

    # Students, in order of prestege
        if bUniversity:
            bPolytech = False
            bCollege = False
            dService_demands["ED7-PAX"] += 1

        if bPolytech:
            bCollege = False
            dService_demands["ED6-PAX"] += 1

        if bCollege:
            dService_demands["ED5-PAX"] += 1

    # Compulsory preschool?
        fRnd = random.random()
        if fRnd < fPreschool:
            bPreschool = True
        else:
            bPreschool = False

    # Standard or private school?
        fRnd = random.random()
        if (fRnd < fPvt_school) and bSchool and not bDisabled_child:
            # Private or religious school, for school going,
            # non-disabled children
            dService_demands["ED4-PAX"] += 1
            bHigh = False
            bMiddle = False
            bPrimary = False
            bPreschool = False

    # High school:
        if bHigh:
            dService_demands["ED3-PAX"] += 1

        if bMiddle:
            dService_demands["ED2-PAX"] += 1

        if bPrimary:
            dService_demands["ED1-PAX"] += 1

        if bToddler and bPreschool:
            dService_demands["ED0-PAX"] += 1
    # End of children

# SORT OUT THE WIFE:
    # Wife in jail:
    fRnd = random.random()
    if fRnd < fPrison:
        dService_demands["YXA-PAX"] += 1
        return dService_demands

    # Wife in nursing home:
    fRnd = random.random()
    if fRnd < fNursing_home:
        if sIncome == "r":
            dService_demands["OAR-PAX"] += 1
        else:
            dService_demands["OAH-PAX"] += 1

    # Housewife by necessity (disabled child)
    if bHousewife:
        # She is not classified as 'unemployed'
        return dService_demands

    # Housewife by choice
    fRnd = random.random()
    if fRnd < fHousewife:
        dService_demands["aUNE-PAX"][sIncome] += 1 # Unemployed cntr
        return dService_demands

    dService_demands["misc"] = "spouse is working"
    return dService_demands

    # Wife contributes to the economy
    if own_gender == "m":
        opp_gender = "f"
    else:
        opp_gender = "m"
    dWorkforce_copy[sIncome + opp_gender] -= 1       # Take one from their list
    if dWorkforce_copy[sIncome + opp_gender] < 0:
        dService_demands["aUNE-PAX"][sIncome] += 1 # Sorry, unemployed

#-------------------------------------------------------------------------------
def qZero_demogfx():
    """ Provides the zeroed out demographics array"""
    dService_demands = {
        "iTOT-PAX": 0,                                      # Total population
        "aHHM-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Married people
        "aHHR-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Married retirees

        "aHHB-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Unmarried people
        "aHHO-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Single retirees

        "aHHX-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Caregiver spouse
        "aHHD-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Disabled 18 ~ 25
        "aUNE-PAX": {"r":0, "h":0, "m":0, "l":0, "p":0},    # Can work but dont

    # EDUCATION (ED?)
        "ED0-PAX": 0,       # Preschool students
        "ED1-PAX": 0,       # Primary school students
        "ED2-PAX": 0,       # Middle school students
        "ED3-PAX": 0,       # High school students
        "ED4-PAX": 0,       # Religious / Private School students
        "ED5-PAX": 0,       # College students
        "ED6-PAX": 0,       # Polytechnic students
        "ED7-PAX": 0,       # University students
        "ED8-PAX": 0,       # RFU (Reserved for future use)
        "ED9-PAX": 0,       # Disabled school

    # DIRECT NURSING
        "OAR-PAX": 0,       # Nursing home for the rich, patients
        "OAH-PAX": 0,       # Standard nursing home
        "OAN-PAX": 0,       # Old Age Nurse OR nurse to disabled person

    # PRISON
        "YXJ-PAX": 0,       # Juvenile detention
        "YXA-PAX": 0,       # Adult prison

    # RELIGION
        "aREL-PAX": {},     # Number of believers in a certain religion

    # TRANSPORT
        "VEH-BIC": 0,       # Total number of bicycles
        "VEH-MBK": 0,       # Total number of motorbikes
        "VEH-CAR": 0,       # Total number of cars
        "VEH-AIR": 0,       # Total number of aircraft (needing an airfield)
        "BUS-PAX": 0,       # Number of passangers requiring public transport
        "misc":""           # To pass messages.
    }

    return dService_demands

#-------------------------------------------------------------------------------
def qHhold_demands(ccTremb, sGeo_code):
    """ This method does the actual work, of building families. It has been
    seperated out as to allow for it to be invoked automatically and without
    operator prompts. Often, the city needs to be rebalanced. Method writes the
    'aDemand_hholds' field with data """
    import random
    import math             # For the ceil-ing function

# WORKFORCE DEMAND EXTRACTION AND GEOCODE VERIFICATION:

    cDest = db.destinations(ccTremb)
    # Look-up the geocode
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

    # Obtain the workforce required
    dDemand_workforce = dGeo_element["aDemand_workforce"]["total"]

# ACCESS THE DEMOGRAPHICS DATA BASE
    cDemo = db.demogfx_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dDemo_harvest = cDemo.find(xParam, xRestr)

    dDfx = {}
    for dQuery in dDemo_harvest:
        for xKey, xVal in dQuery.items():
            dDfx[xKey] = xVal    # Copy out the data


# MANIPULATE DATA
    # A copy or a duplicate is needed, since there will be people of this type
    # added. Some workers may be bringing in a partner who does not have work
    # in this town.
    dWorkforce_copy = dDemand_workforce.copy()

    # Itemise where the demand is.
    dService_demands = qZero_demogfx()

    for sIncome in ["r", "h", "m", "l", "p"]:
        iMale = dWorkforce_copy[sIncome + "m"]
        iFemale = dWorkforce_copy[sIncome + "f"]
        iBoth = iMale + iFemale
        if iBoth == 0: continue         # Don't bother with empty groups

        # See if the protagonist needs to be jailed OR in a nursing home
        for x in range(iBoth):
            # Prison
            fRnd = random.random()
            if fRnd < dDfx["prison_rate"]:
                dService_demands["YXA-PAX"] += 1
                continue

            # Nursing home
            fRnd = random.random()
            if fRnd < dDfx["nursing_home_rate"]:
                if sIncome == "r":
                    dService_demands["OAR-PAX"] += 1
                else:
                    dService_demands["OAH-PAX"] += 1

        # Go through every man to see if he needs to be married.
        for x in range(iMale):
            dDataIn = {
                "dDfx": dDfx,
                "dService_demands": dService_demands,
                "sIncome": sIncome,
            }
            dService_demands = qThe_hhold_demands(dDataIn)
            if dService_demands["misc"] == "spouse is working":
                iFemale -= 1
                if iFemale <= 0:
                    dService_demands["aUNE-PAX"][sIncome] += 1 # unemployed

        # Go through the women that are the head of household
        if iFemale > 0:
            for x in range(iFemale):
                dDataIn = {
                    "dDfx": dDfx,
                    "dService_demands": dService_demands,
                    "sIncome": sIncome,
                }
                dService_demands = qThe_hhold_demands(dDataIn)
                if dService_demands["misc"] == "spouse is working":
                    iMale -= 1
                    if iMale <= 0:
                        dService_demands["aUNE-PAX"][sIncome] += 1 # unemployed

    # RETIREES:
        # Get the working age adults together
        iWa_married = dService_demands["aHHM-PAX"][sIncome]
        iWa_single = dService_demands["aHHB-PAX"][sIncome]
        iWa_total = iWa_married + iWa_single

        # Calculate how many retirees I need.
        iWork_delta = dDfx["max_work_age"] - dDfx["min_work_age"]     # 65-19=46
        fWork_life = iWork_delta / dDfx["life_expect"]           # 46/80 = 0.575
        fTot_exp_group = iWa_total / fWork_life               # All ages 0 to 80
        iRet_delta = dDfx["life_expect"] - dDfx["max_work_age"]       # 80-65=15
        fRet_life = iRet_delta / dDfx["life_expect"]            # 15/80 = 0.1875
        fNo_of_ret = fTot_exp_group * fRet_life                # 18% of all ages
        iTot_ret = int(round(fNo_of_ret, 0))             # Round off and convert

        # See if the protagonist needs to be jailed OR in a nursing home
        iOah_ret = 0
        iYxa_ret = 0            # Jailed retiree
        for x in range(iTot_ret):
            # Prison
            fRnd = random.random()
            if fRnd < dDfx["prison_rate"]:
                dService_demands["YXA-PAX"] += 1
                iYxa_ret += 1
                continue

            # Nursing home. NOTE that the chances of being in a nursing home
            # have been increased.
            fRnd = random.random()
            if fRnd < (dDfx["nursing_home_rate"] * 1.75):
                if sIncome == "r":
                    dService_demands["OAR-PAX"] += 1
                else:
                    dService_demands["OAH-PAX"] += 1
                iOah_ret += 1        # To take away from the general counter
                continue

        iTot_ret -= iOah_ret

        fCpl_ret = iTot_ret * dDfx["aPartners"][sIncome] / 2.0
        iCpl_ret = int(round(fCpl_ret, 0)) * 2

        # retired singles:
        iSgl_ret = iTot_ret - iCpl_ret
        # Retirees don't need a large garden; they would be content in a apt.
        dService_demands["aHHR-PAX"][sIncome] += iCpl_ret
        dService_demands["aHHO-PAX"][sIncome] += iSgl_ret

    # End of income level
    # Calculate the total population and setup religion of adults:
    iTot_pax = 0
    dReligion = {}
    for denomination in dDfx["aaReligion"]:
        sCode = denomination["code"]                # Extract the religion code
        dReligion[sCode] = 0                    # Make a zero list of the codes

# DO THE FINAL RESULTS
    for sIncome in ["r", "h", "m", "l", "p"]:
        iTot_group = 0
        # POPULATION TOTAL

        # FREE ADULTS
        for sClass in [

            "aHHM-PAX", "aHHR-PAX", "aHHB-PAX", "aHHO-PAX", "aHHD-PAX"]:
            # Married workers, Bachelor workers, Married retirees,
            # Golden Oldies unmaried retirees, Disabled 18 to 25 year olds
            iTot_group += dService_demands[sClass][sIncome]     # For the church
            iTot_pax += dService_demands[sClass][sIncome]
        # RELIGION
        for denomination in dDfx["aaReligion"]:
            sCode = denomination["code"]            # "3R", "AN", ...
            fRatio = denomination[sIncome]          # Demographic group
            fCongragation = iTot_group * fRatio
            iCongragation = int(round(fCongragation, 0))
            dReligion[sCode] += iCongragation       # Add up across demographics

    # DEMAND FOR WORSHIP
    dService_demands["aREL-PAX"] = dReligion

    # OLD-AGE HOME RESIDENTS
    iTot_pax += dService_demands["OAR-PAX"]     # The rich
    iTot_pax += dService_demands["OAH-PAX"]     # The normal

    # Children
    for iLevel in range (0, 10):
        sClass = "ED{0}-PAX".format(iLevel)
        iTot_pax += dService_demands[sClass]

    # Prisoners
    # Place them on the account of the 'host' city

    dService_demands["iTOT-PAX"] = iTot_pax
    dService_demands["misc"] = None

# CALCULATE THE ACTUAL DEMAND
    dTot_hhold_dmd = {}
    iHhold_road_veh = 0          # Calculate how many private vehicles are there
    for sIncome in ["r", "h", "m", "l", "p"]:
        # WORKING MARRIED HOUSEHOLDS
        iHhm_pax = dService_demands["aHHM-PAX"][sIncome]
        fHhm_hh = iHhm_pax / 2.0                # Two people per household
        iHhm_hh = int(math.ceil(fHhm_hh))

        # RETIRED MARRIED HOUSEHOLDS
        iHhr_pax = dService_demands["aHHR-PAX"][sIncome]
        fHhr_hh = iHhr_pax / 2.0                # Two people per household
        iHhr_hh = int(math.ceil(fHhr_hh))

        dTot_hhold_dmd[sIncome] = iHhm_hh + iHhr_hh

        # WORKING BACHELOR HOUSEHOLDS
        iHhb_pax = dService_demands["aHHB-PAX"][sIncome]
        fFrat_hh = iHhb_pax / dDfx["fraternal_rate"]    # 1.9 bachelors per hh
        iFrat_hh = int(math.ceil(fFrat_hh))

        # RETIRED NON-MARRIED HOUSEHOLDS
        iHho_pax = dService_demands["aHHO-PAX"][sIncome]
        fOldies_hh = iHho_pax / dDfx["fraternal_rate"]  # 1.9 per household
        iOldies_hh = int(math.ceil(fOldies_hh))
        dTot_hhold_dmd[sIncome] += iFrat_hh + iOldies_hh

    # VEHICLE COUNTS
        fRet = dDfx["aaVehicles"]["retiree_derate"]
        fBac = dDfx["aaVehicles"]["bachlelor_derate"]

        # Loop through eac of the categories
        for iCnt in range(4):
        # Select the transport technology
            # Bicycle
            if iCnt == 0:
                fType = dDfx["aaVehicles"]["aBicycle"][sIncome]
                sVeh_type = "VEH-BIC"

            # Motorbike
            elif iCnt == 1:
                fType = dDfx["aaVehicles"]["aMotorbike"][sIncome]
                sVeh_type = "VEH-MBK"

            # Car
            elif iCnt == 2:
                fType = dDfx["aaVehicles"]["aCar"][sIncome]
                sVeh_type = "VEH-CAR"

            # Vehicle
            elif iCnt == 3:
                fType = dDfx["aaVehicles"]["aAircraft"][sIncome]
                sVeh_type = "VEH-AIR"

        # MARRIED WORKING HOUSEHOLD
            fFactor = fType
            fNo_of_veh = dService_demands["aHHM-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dService_demands[sVeh_type] += iNo_of_veh

        # MARRIED RETIRED HOUSEHOLD
            fFactor = fType * fRet
            fNo_of_veh = dService_demands["aHHR-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dService_demands[sVeh_type] += iNo_of_veh

        # BACHELOR WORKING HOUSEHOLD
            fFactor = fType * fBac
            fNo_of_veh = dService_demands["aHHB-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dService_demands[sVeh_type] += iNo_of_veh

        # MARRIED RETIRED HOUSEHOLD
            fFactor = fType * fRet * fBac
            fNo_of_veh = dService_demands["aHHR-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dService_demands[sVeh_type] += iNo_of_veh

    # DEMAND FOR PUBLIC TRANSPORT
#        "BUS-PAX": 0,       # Number of passangers requiring public transport

    # UPDATE THE VEHICLES ITEM
    aVehicles = dGeo_element["aVehicles"]           # The full element
    iNew_vehicles = 0                               # Requiring numberplates
    iNew_vehicles += dService_demands["VEH-MBK"]    # Motorbike
    iNew_vehicles += dService_demands["VEH-CAR"]    # Cars

    iLen = len(aVehicles)
    if iLen == 1:            # Only 'tot_road' item is there,
        aVehicles["aItemised"] = {}               # Add a layer

    # Update the existing elements. Add 'town' to the itemised elements
    aVehicles["aItemised"]["residents"] = iNew_vehicles

    iTot_road = 0
    for iItem in aVehicles["aItemised"]:
        iTot_road += aVehicles["aItemised"][iItem]
    aVehicles["tot_road"] = iTot_road


# UPDATE ALL THE DATA
    xParam = {"geo_code":sGeo_code}
    xNew_data = {"$set": {
            "aDemand_hholds": dTot_hhold_dmd,
            "aDemographics": dService_demands,
            "aVehicles": aVehicles}}
    cDest.update_one(xParam, xNew_data)

    return iTot_pax

#-------------------------------------------------------------------------------

def household_demands(ccTremb):
    """ Builds household demands manually. It prompts the user to enter the
    geo-code of the area. Method will then delegate the calculation where the
    statistics will be entered into the 'aDemand_hholds' field."""
# GEOCODE
    # Enter the geo code for the area in question
    sTxt = ("\nPlease enter the geo-code ('GYN-G' for example) for the area" +
            " in question")
    print(sTxt)
    sGeo_code = input().upper()
    xResp = qHhold_demands(ccTremb, sGeo_code)
    if xResp == None:
        return None

#-------------------------------------------------------------------------------
# M: ADD A MAP
#-------------------------------------------------------------------------------
def add_map_to_db(ccTremb):
    """ Adds a map to its database. These give a point of reference to the
    systems"""
    dNew_map = {
        "sRegion": None,
        "iYear": None,
        "fScale": None,
    }

    # Region name
    sTxt = ("\nEnter the name of the region in Latin "
            +"(International Keybord allowed)")
    print(sTxt)
    dNew_map["sRegion"] = input()                                 # "Trembovice"

    # Year of first drawing
    sTxt = "\nEnter the year real-world year when the map was first drawn"
    print(sTxt)
    dNew_map["iYear"] = input()                                           # 2012

    # Map scale, which needs to be a valid float
    sTxt = "\nEnter the scale of the map (scientific notation '4e6' is accepted)"
    print(sTxt)
    sScale = input()                                                      # 20e6
    try:
        fScale = float(sScale)
        dNew_map["fScale"] = fScale
    except Exception as e:
        print(e)
        print("\nExiting without saving. "
             +"Please try again to enter a floating point number")
        return None

    # Entry confirmation
    sTxt = "Is this entry OK? (Press 'Y' or 'N')\n{0}"
    print(sTxt.format(dNew_map))
    sInput = input().upper()
    if sInput != "Y":
        print("\nConfirmation failed. Not added to the database")
        return None

    # Do the database query
    cMap = db.maps_db(ccTremb)
    cMap.insert_one(dNew_map)

#-------------------------------------------------------------------------------
# S: ADD CITY SERVICE DEMANDS
#-------------------------------------------------------------------------------
def qServices_demands(ccTremb, sGeo_code):
    """ This routine does the actual work of calculating the number of policemen
    and their management. However, it does not 'build' a police station, as it
    could be shared with a neighbouring area"""

# EXTRACT THE FULL ENTRY CONTAINING THE GEO-CODE
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

# ACCESS THE SERVICES DATABASE:
    cDb = db.city_services_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dDatabase = cDb.find(xParam, xRestr)

    aSvc = []
    for dQuery in dDatabase:
        aSvc.append(dQuery)

# MANIPULATE DATA
    # Get a list of services already itemised:
    # NOTE OF CAUTION: These are reference linked. Hence, changes are reflected
    # back into the dGeo_element-object.
    aItemised = dGeo_element["aDemand_workforce"]["aItemised"]
    aVeh_Item = dGeo_element["aVehicles"]["aItemised"]

    # ENSURE THAT STATIC WORKPLACES (LIKE A WHEAT FARM) HAVE A CODE ASSIGNED.
    cWkp = db.workplaces_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dDatabase = cWkp.find(xParam, xRestr)

    # Go through the database and make sure that the code does exist.
    for dWkp in dDatabase:
        for dItem in aItemised:
            if "sCode" in dItem.keys():
                continue            # Already sorted out

            # Exact match on the name
            if dItem["sName"] == dWkp["default"]:
                dItem["sCode"] = dWkp["code"]    # Add the code to the structure
                continue

            # Name has different case
            if dItem["sName"].lower() == dWkp["default"].lower():
                dItem["sCode"] = dWkp["code"]    # Add the code to the structure
                dItem["sName"] = dItem["sName"].lower()
                continue
        # End of going through each itemised workplace
    # end of going through all the registered workplaces

    # ITERATE THROUGH ALL THE STANDARD SERVICES
    for dSvc in aSvc:
        sItem_name = dSvc["name"]               # "Police"
        aVeh_Item[sItem_name] = 0               # Public regisered vehicles

        # REMOVE THE PREVIOUS ITEM FROM THE STACK.
        # the 'del'-command reduces the size of the list. Consequently, the
        # initially-specified number of iterations cause an index error on the
        # last item. Hence, the number of items are counted up-front and the
        # number of iterations is adjusted accordingly. This however causes an
        # unexpected issue: If the item of interest is the last one in the list,
        # it will be missed. To avoid missing it, we need to take pro-active
        # action and remove it first.

        sTarget_name = sItem_name.lower()                # Make case insensitive
        sThis_name = aItemised[-1]["sName"].lower()      # Extract the last item
        if sTarget_name == sThis_name:
            del aItemised[-1]                        # Remove object of interest

        # count the number of duplicates
        iTot_items = len(aItemised)
        iNo_of_items = 0
        for iCnt in range(iTot_items):
            sThis_name = aItemised[iCnt]["sName"].lower()
            if sThis_name == sTarget_name:
                iNo_of_items += 1

        iTot_items = len(aItemised)
        iTot_items -= iNo_of_items  # Guard against running out of indexes
        for iCnt in range(iTot_items):
            sThis_name = aItemised[iCnt]["sName"].lower()
            sTarget_name = sItem_name.lower()

            if sThis_name == sTarget_name or sThis_name == "preschool":
                del aItemised[iCnt]             # It will be rebuilt

        # Build up the new item.
        dThe_item = {
            "sCode": dSvc["code"],
            "sName": sItem_name,
            "rm":0, "rf":0, "hm":0, "hf":0, "mm":0, "mf":0,
            "lm":0, "lf":0, "pm":0, "pf":0, "iVeh_cnt":0
        }

        # Get the hinge demographic: effectively, how many of these per one
        # service person. In the example of the police, it is the total
        # population which determines the number of police officers on the
        # ground.
        sServes = dSvc["serves"]
        if sServes not in dGeo_element["aDemographics"]:
            print("\n'{0}' service item '{1}' not found in '{2}'\a".format(
                sItem_name, sServes, sGeo_code))
            return None

        # Calculate the number of 'main' service providers
        xService_value = dGeo_element["aDemographics"][sServes]
        fBase_ratio = dSvc["ratio"]      # 200 citizens : 1 policeman
        fBase_number = xService_value / fBase_ratio
        iMain_cnt = int(round(fBase_number, 0))

        # Do the gender split
        xType1 = dSvc["aMain"]["xType1"].lower()
        xType2 = dSvc["aMain"]["xType2"].lower()
        iRate1 = dSvc["aMain"]["iRate1"]
        iRate2 = dSvc["aMain"]["iRate2"]

        # Calculate the first demographic
        fCount1 = iMain_cnt * iRate1 / 100.0
        iCount1 = int(round(fCount1, 0))
        dThe_item[xType1] += iCount1

        # Calculate the second demographic
        fCount2 = iMain_cnt * iRate2 / 100.0
        iCount2 = int(round(fCount2, 0))
        dThe_item[xType2] += iCount2

        # Number of "squad" cars:
        fEmpl_per_veh = dSvc["aMain"]["fEmpl_per_veh"]
        if fEmpl_per_veh == 0:
            iNo_of_veh = 0
        else:
            fNo_of_veh = iMain_cnt / fEmpl_per_veh
            iNo_of_veh = int(round(fNo_of_veh, 0))
        dThe_item["iVeh_cnt"] += iNo_of_veh

        # A 'cheap' way of doing OR
        if dSvc["sOwn_number_plates"] in ["none", "static"]:
            # Public numberplates (not police plates like 'YG')
            aVeh_Item[sItem_name] += iNo_of_veh

    # DO SUPERVISORS, MANAGERS AND SUPPORT STAFF
        for sTitle in ["aSupv", "aMgmt", "aSupt"]:
            fBase_ratio = dSvc[sTitle]["fMain_per_empl"]  # 10 cops / 1..
            if fBase_ratio == 0:
                continue        # This level is not used
            fBase_number = iMain_cnt / fBase_ratio
            iEmpl_cnt = int(round(fBase_number, 0))

            # Do the gender split
            xType1 = dSvc[sTitle]["xType1"].lower()
            xType2 = dSvc[sTitle]["xType2"].lower()
            iRate1 = dSvc[sTitle]["iRate1"]
            iRate2 = dSvc[sTitle]["iRate2"]

            # Calculate the first demographic
            fCount1 = iEmpl_cnt * iRate1 / 100.0
            iCount1 = int(round(fCount1, 0))
            dThe_item[xType1] += iCount1

            # Calculate the second demographic
            fCount2 = iEmpl_cnt * iRate2 / 100.0
            iCount2 = int(round(fCount2, 0))
            dThe_item[xType2] += iCount2

            # Number of "squad" cars:
            fEmpl_per_veh = dSvc[sTitle]["fEmpl_per_veh"]
            if fEmpl_per_veh == 0:
                iNo_of_veh = 0
            else:
                fNo_of_veh = iEmpl_cnt / fEmpl_per_veh
                iNo_of_veh = int(round(fNo_of_veh, 0))
            dThe_item["iVeh_cnt"] += iNo_of_veh

            # Public (County registered) or Government (Y-plates) registered?
            if dSvc["sOwn_number_plates"] in ["none", "static"]:
                # Public numberplates (not police plates like 'YG')
                aVeh_Item[sItem_name] += iNo_of_veh
        # END OF DYNAMIC STAFF ASSIGNMENT

        # Public (County registered) or Government (Y-plates) registered?
        if dSvc["sOwn_number_plates"] in ["none", "dynamic"]:
            # Public numberplates (not police plates like 'YG')
            # The police can have some civilian registerd vehicles.
            aVeh_Item[sItem_name] += dSvc["iStatic_veh"]
        dThe_item["iVeh_cnt"] += dSvc["iStatic_veh"]

        # Add the new item to the list
        aItemised.append(dThe_item)             # NOTE reference link.
    # END OF GOING THROUGH STANDARD SERVICES.

    # Recalculate the new workforce demands
    aDemand_workforce = dGeo_element["aDemand_workforce"]
    dNew_total = {}
    for sIncome in ["r", "h", "m", "l", "p"]:
        for sGender in ["m", "f"]:
            dNew_total[sIncome + sGender] = 0  # Clear the counters.

    # Calculate the new workforce totals
    for dItem in aItemised:
        for sCode in dNew_total:
            dNew_total[sCode] += dItem[sCode]
    dGeo_element["aDemand_workforce"]["total"] = dNew_total

    # Recalculate the vehicle totals
    iTot_veh = 0
    for sVeh in aVeh_Item:
        iTot_veh += aVeh_Item[sVeh]
    dGeo_element["aVehicles"]["tot_road"] = iTot_veh

    # SAVE IT IN THE DATABASE
    xParam = {"geo_code":sGeo_code}
    xNew_data = {"$set": {
        "aDemand_workforce": dGeo_element["aDemand_workforce"],
        "aVehicles": dGeo_element["aVehicles"]
    }}

    cDest.update_one(xParam, xNew_data)
    return True

#-------------------------------------------------------------------------------
def add_services_demand(ccTremb):
    """ Adds policemen, teachers, ect to the workforce demand. This routine
    asks for the geo-code, which will be passed to its delegate. The delegate
    has the option of being invoked automatically."""

# GEOCODE
    # Enter the geo code for the area in question
    sTxt = ("\nPlease enter the geo-code ('GYN-G' for example) for the area" +
            " in question")
    print(sTxt)
    sGeo_code = input().upper()
    xResp = qServices_demands(ccTremb, sGeo_code)
    if xResp == None:
        return None

#-------------------------------------------------------------------------------
# U: UPDATE PARENT WITH CHILDREN'S DATA
#-------------------------------------------------------------------------------
def qqParent_update(ccTremb, dParent):
    """ RECURSIVE function that reads the children and updates the parent. Data
    passed up is:
        demand workforce total,
        supply workforce total,
        demand households total,
        supply households total,
        demographics,
        vehicle totals,
        warehouse totals.
    Each child's total is itemised, where applicable.
    """

    # Bring up the list of children.
    aChildren = dParent["aChildren"]
    sParent_id = dParent["my_id"]           # To be verified with the child
    iNo_of_children = len(aChildren)

    # Don't bother any further if there are no children registered
    if iNo_of_children == 0:
        return iNo_of_children

    # Gain access to the database
    cDest = db.destinations(ccTremb)

# CLEAR PARENT'S TOTALS.
    # DEMAND WORKFORCE
    dParent["aDemand_workforce"]["total"] = {
        "rm":0, "hm":0, "mm": 0, "lm":0, "pm":0,
        "rf":0, "hf":0, "mf": 0, "lf":0, "pf":0,
        "iVeh_cnt": 0
    }
    dParent["aDemand_workforce"]["aItemised"] = []

    # SUPPLY WORKFORCE
    # RFU: Reserved for future use. It was initially designed with the same
    # structure as the demand. However, it has lost its meaning. More
    # meaningful is the 'supply_hholds', element which balances the household
    # demands.

    # DEMAND HOUSEHOLDS
    # Which areas demand what type of 'class' of person
    dParent["aDemand_hholds"] = {
        "total": {"r":0, "h":0, "m":0, "l":0, "p":0},
        "aItemised":[]}

    # SUPPLY HOUSEHOLDS
    # Where do the 'classes' live
    dParent["aSupply_hholds"] = {
        "total": {"r":0, "h":0, "m":0, "l":0, "p":0},
        "aItemised":[]}

    # DEMOGRAPHICS
    # Who do I have in my city?
    dParent["aDemographics"] = qZero_demogfx()
    dParent["aDemogfx_item"] = []       # Itemised elements of the demographics

    # VEHICLES
    # How many number plates are needed?
    dParent["aVehicles"] = {
        "tot_road":0,
        "aItemised":{}
    }

    # FOOTPRINT
    dParent["aFootprint"] = {}

    # WAREHOUSE
    dParent["aWarehouse"] = {}
    dParent["aWhs_item"] = []

# GO THROUGH EACH CHILD
    for sChild_id in aChildren:
        # Verify the identifier. Children are itentified by their ids
        xParam = {"my_id":sChild_id}
        xRestr = {"_id":0}
        dGeo_query = cDest.find(xParam, xRestr)

        # Look at the results of the query
        iNo_of_hits = 0
        aName = {}

        for query in dGeo_query:
            iNo_of_hits += 1
            dChild = query

        if iNo_of_hits != 1:
            sTxt = "\n\a'My_id' ({0}) verification failed. Exiting"
            print(sTxt.format(sChild_id))
            return None

    # Check if we are a grand-parent:
        # /!\ RECURSION /!\
        iNo_of_grandchildren = qqParent_update(ccTremb, dChild)
        if iNo_of_grandchildren == None: return None    # Propagate error

# CHILD GEO-CODE:
        sChild_geo = dChild["geo_code"]

# DEMAND WORKFORCE:
        dChd_dmd_wkf = dChild["aDemand_workforce"]
    # Road vehicles
        # There is an issue here. When the children are balanced, the total
        # number of vehilces (government and county plates) are not stored in
        # the total.
        # On the parent level, I would like to have that information. Hence,
        # I need to go through the child's item list and extract that data.
        iVeh_cnt = 0
        for iItem in dChd_dmd_wkf["aItemised"]:
            iVeh_cnt += iItem["iVeh_cnt"]

    # Itemisation
        dItem = {}                              # Build for the itemised logging
        dItem["sName"] = sChild_geo

        for sGroup in dChd_dmd_wkf["total"]:
            # For the itemised list
            dItem[sGroup] = dChd_dmd_wkf["total"][sGroup]   # Transfer individ
            # For the grand-total on the parent:
            dParent["aDemand_workforce"]["total"][sGroup] += dItem[sGroup]
        # Vehicles are not included in the child's totals
        dItem["iVeh_cnt"] = iVeh_cnt
        dParent["aDemand_workforce"]["total"]["iVeh_cnt"] += iVeh_cnt

        # Save the itemised list with the parent
        dParent["aDemand_workforce"]["aItemised"].append(dItem)

# SUPPLY WORKFORCE:
    # RFU

# DEMAND HOUSEHOLDS:
        dChd_dmd_hhd = dChild["aDemand_hholds"]
        # There is a change in the structure of this item, between the 'empty' and
        # 'full' versions.
        if "total" in dChd_dmd_hhd.keys():
            dChd_dmd_hhd = dChd_dmd_hhd["total"]

        dItem = {}
        dItem["sName"] = sChild_geo
        for sGroup in dChd_dmd_hhd:
            dItem[sGroup] = dChd_dmd_hhd[sGroup]
            dParent["aDemand_hholds"]["total"][sGroup] += dItem[sGroup]

        # Push into the itemised section
        dParent["aDemand_hholds"]["aItemised"].append(dItem)

# SUPPLY HOUSEHOLDS:
        dChd_sup_hhd = dChild["aSupply_hholds"]
        # There is a change in the structure of this item, between the 'empty' and
        # 'full' versions.
        if "total" in dChd_sup_hhd.keys():
            dChd_sup_hhd = dChd_sup_hhd["total"]

        dItem = {}
        dItem["sName"] = sChild_geo
        for sGroup in dChd_sup_hhd:
            dItem[sGroup] = dChd_sup_hhd[sGroup]
            dParent["aSupply_hholds"]["total"][sGroup] += dItem[sGroup]

        # Push into the itemised section
        dParent["aSupply_hholds"]["aItemised"].append(dItem)

# DEMOGRAPHICS:
        dChd_demogfx = dChild["aDemographics"]
        dPrt_demogfx = dParent["aDemographics"]

        # Check if the demographics have been generated
        if dChd_demogfx != {}:
            dItem = {}
            dItem["sName"] = sChild_geo
            dItem["sLat"] = dChild["aName"]["lat"]
            dItem["sCyr"] = dChild["aName"]["cyr"]

            # Non-educational totals
            aItem_list = [
                "iTOT-PAX",         # Total population
                "OAR-PAX",          # Rich old age home bed demand
                "OAH-PAX",          # Standard old age home bed demand
                "OAN-PAX",          # Demand for personal nurse
                "YXJ-PAX",          # Juvenile prison 'seat' demand
                "YXA-PAX",          # Adult prison 'seat' demand
                "VEH-BIC",          # Number of bicycles
                "VEH-MBK",          # Number of motorbikes (county number plates)
                "VEH-CAR",          # Number of cars (county number plates)
                "BUS-PAX"           # Number of possible commuters.
            ]

            for sItem in aItem_list:
                dItem[sItem] = dChd_demogfx[sItem]    # Total population
                dPrt_demogfx[sItem] += dItem[sItem]

            # Class-based statistics
            aGroup_list = [
                "aHHM-PAX",         # Married and working people
                "aHHR-PAX",         # Married and retired people
                "aHHB-PAX",         # Working bachelors (both genders)
                "aHHO-PAX",         # "Golden Oldies": Retired and not married
                "aHHX-PAX",         # Stay-at-home people (nursing or children)
                "aHHD-PAX",         # Disabled people not in a nursing home
                "aUNE-PAX",         # Unemployed, but willing to work
            ]

            for sItem in aGroup_list:
                dItem[sItem] = {}
                for sGroup in ["r", "h", "m", "l", "p"]:
                    iValue = dChd_demogfx[sItem][sGroup]
                    dItem[sItem][sGroup] = iValue      # For itemised billing
                    dPrt_demogfx[sItem][sGroup] += iValue

            # Itemise the total number of students at all levels
            for iCnt in range(10):
                sSchool = "ED{0}-PAX".format(iCnt)
                dItem[sSchool] = dChd_demogfx[sSchool]
                dPrt_demogfx[sSchool] += dItem[sSchool]

        # Religions
            dChd_rel = dChd_demogfx["aREL-PAX"]
            dPrt_rel = dPrt_demogfx["aREL-PAX"]
            dItem["aREL-PAX"] = dChd_rel

            # Loop through each of the religions
            for sRel_code in dChd_rel:
                # If it is the first time, then create the religious key
                if sRel_code not in dPrt_rel.keys():
                    dPrt_rel[sRel_code] = dChd_rel[sRel_code]
                else:
                    dPrt_rel[sRel_code] +=dChd_rel[sRel_code]
        # DEMOGRAPHICS DON'T EXIST
        else:
            dParent["aDemographics"]["misc"] = "Incomplete Data"
            dItem = {}
            dItem["sName"] = sChild_geo
            dItem["sLat"] = dChild["aName"]["lat"]
            dItem["sCyr"] = dChild["aName"]["cyr"]
        dParent["aDemogfx_item"].append(dItem)

# VEHICLES:
        dChd_veh = dChild["aVehicles"]
        dPrt_veh = dParent["aVehicles"]

        # Check if the vehicles have been generated
        if dChd_veh != {}:
            dPrt_veh["aItemised"][sChild_geo] = dChd_veh['tot_road']
            dPrt_veh["tot_road"] += dChd_veh['tot_road']

        # No vehicles registered with the child. Do nothing
        else:
            pass

# FOOTPRINT
        dChd_ftp = {
            "val": dChild["aArea"]["qty"],      # Value of the area
            "uom": dChild["aArea"]["uom"]       # units of measure
        }
        dParent["aFootprint"][sChild_geo] = dChd_ftp

# WAREHOUSE
        dPrt_whs = dParent["aWarehouse"]
        dChd_whs = dChild["aWarehouse"]
        for dItem in dChd_whs:
            dContent = dChd_whs[dItem]
            resource = dContent["resource"].lower()
            amount = dContent["annual_output"]
            units = dContent["units"]

            dItemised = {}
            dItemised["sName"] = sChild_geo
            dItemised["resource"] = resource
            dItemised["amount"] = amount
            dItemised["units"] = units

            dParent["aWhs_item"].append(dItemised)

            # Create a new entry
            if dPrt_whs == {}:
                dPrt_whs["Warehouse 0"] = {}
                dPrt_whs["Warehouse 0"]["resource"] = resource
                dPrt_whs["Warehouse 0"]["annual_output"] = amount
                dPrt_whs["Warehouse 0"]["units"] = units
            # We need to update the existing data
            else:
                bNot_found = True               # We don't store this yet.
                iIdx = 0
                for dProduct in dPrt_whs:
                    dProd_data = dPrt_whs[dProduct] # 'Warehouse 0' is ...
                    sWhat_is_it = dProd_data["resource"].lower()
                    if sWhat_is_it != resource:
                        iIdx += 1               # If we have to build warehouse
                        continue                # Go to the next product
                    if dProd_data["units"] != units:
                        print("\n\aUnits mismatch at the warehouse. EXITING")
                        return None
                    # Good to go, add up the items.
                    fSub_tot = dProd_data["annual_output"] + amount
                    dProd_data["annual_output"] = round(fSub_tot, 3)
                    bNot_found = False

                # We need a new warehouse:
                if bNot_found == True:
                    sWhs_name = "Warehouse {0}".format(iIdx)
                    dPrt_whs[sWhs_name] = {}
                    dPrt_whs[sWhs_name]["resource"] = resource
                    dPrt_whs[sWhs_name]["annual_output"] = amount
                    dPrt_whs[sWhs_name]["units"] = units

# UPDATE ALL THE DATA
    # Note that items "aDemogfx_item" and "aWhs_item" give too much information.
    # They have been removed from the final write.
    xParam = {"geo_code":dParent["geo_code"]}
    xNew_data = {"$set": {
            "aDemand_workforce": dParent["aDemand_workforce"],
            "aDemand_hholds": dParent["aDemand_hholds"],
            "aSupply_hholds": dParent["aSupply_hholds"],
            "aDemographics": dParent["aDemographics"],
        #    "aDemogfx_item": dParent["aDemogfx_item"],
            "aVehicles": dParent["aVehicles"],
            "aFootprint": dParent["aFootprint"],
            "aWarehouse": dParent["aWarehouse"],
        #    "aWhs_item": dParent["aWhs_item"]
            }}
    cDest.update_one(xParam, xNew_data)
    sTxt = "'{0}' has been updated with children's data"
    print(sTxt.format(dParent["geo_code"]))

    return iNo_of_children
#-------------------------------------------------------------------------------
def update_parent(ccTremb):
    """ Goes through all its children and gathers demographic, vehicular and
    industrial information. It itemises each child within the parent."""

# GEOCODE OF PARENT:
    sTxt = ("\nPlease enter the geo-code ('GY' for example) of the parent " +
        "which requests data\nfrom its children.")
    print(sTxt)
    sParent = input().upper()                  # Allow user to type in any case

    # Access the database
    cDest = db.destinations(ccTremb)
    xParam = {"geo_code": sParent}
    xRestr = {"_id":0}
    dParent_query = cDest.find(xParam, xRestr)

    # Verify existance of parent
    iNo_of_hits = 0
    dParent = {}                        # For context breaking
    for my_query in dParent_query:
        iNo_of_hits += 1
        dParent = my_query

    if iNo_of_hits != 1:
        sTxt = "\n\aUnexpected number of geo-codes {0} (expecting 1)"
        print(sTxt.format(iNo_of_hits))
        return None

    # ENTER THE RECURSIVE SYSTEM:
    iNo_of_children = qqParent_update(ccTremb, dParent)
    if iNo_of_children == None: return None


#-------------------------------------------------------------------------------
# W: ADD WORKPLACES, WITH THEIR LABOUR DEMANDS AND RESOURCE OUTPUTS
#-------------------------------------------------------------------------------
def qCalc_non_main_staff(aData):
    """ Method calculates the number of supervisors, managers and support staff
    based on the number of the 'main' employees.
    """
# EXPLODE THE INPUT
    dLabour_element = aData["dLabour_element"]  # Constants for this level
    fTot_main = aData["fTot_main"]              # Number of 'main' staff
    aDemogfx = aData["aDemogfx"]                # Running totals
    sWho = aData["sWho"]                        # "aSupv", "aMgmt" or "aSupt"

# SUPERVISOR DEMOGRAPHIC CALCULATION
    # Calculate the number of supervising / managing / supporting staff
    fGroup_ratio = dLabour_element[sWho]["fRate"]
    if fGroup_ratio == 0:
        fTot_group = 0.0                   # No supervisors
    else:
        fTot_group = (fTot_main / fGroup_ratio)

    # group 1
    xGroup_type = dLabour_element[sWho]["xType1"].lower()
    iGroup_rate = dLabour_element[sWho]["iRate1"]
    fType = (fTot_group * iGroup_rate / 100.0)
    iType = int(round(fType, 0))     # Mind your language! (Don't google 'Ruby')
    aDemogfx[xGroup_type] += iType           # Add to the demographics table

    # group 2
    xGroup_type = dLabour_element[sWho]["xType2"].lower()
    iGroup_rate = dLabour_element[sWho]["iRate2"]
    fType = (fTot_group * iGroup_rate / 100.0)
    iType = int(round(fType, 0))     # Mind your language! (Don't google 'Ruby')
    aDemogfx[xGroup_type] += iType           # Add to the demographics table

    # Vehicle registration
    fEmpl_per_veh = dLabour_element[sWho]["fEmpl_per_veh"]
    if fEmpl_per_veh > 0:
        fVeh_cnt = fTot_group / fEmpl_per_veh        # Rough number of vehicles
        iVeh_cnt = int(round(fVeh_cnt, 0))          # Round and integerise
        aDemogfx["veh_reg"] += iVeh_cnt

    return aDemogfx
#-------------------------------------------------------------------------------
def add_workplace(ccTremb):
    """ Adds the 'industries' which operate in this area. These could be farms,
    offices, factories. Effectively, this creates demand for a workforce.
    """
# GEOCODE
    # Enter the geo code for the area in question
    sTxt = ("\nPlease enter the geo-code ('GYG-H' for example) for the area" +
            " you are adding\nworkplaces to.")
    print(sTxt)
    sGeo_code = input().upper()

    # Get the element. Also verify that the geocode is registered in the data
    # base
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None:
        return None

    # Confirmation message
    sTxt = ("\nYou are adding industry to {0} / {1}")
    dName = dGeo_element["aName"]
    print(sTxt.format(dName["lat"], dName["cyr"]))

# THE TYPE LIST.
    cWorkplace = db.workplaces_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0, "type":1}
    dType_list = cWorkplace.find(xParam, xRestr)

    # Copy out the data from the database.
    aAll = []
    for dQuery in dType_list:
        aAll.append(dQuery["type"])

    # Remove duplicates while preserving the order:
    aType = []
    for sItem in aAll:
        if sItem not in aType:
            aType.append(sItem)

    # Show a menu with the types of industry
    iIdx = 0
    sMenu = "\nPlease select the type of workplace:"
    for choice in aType:
        iIdx += 1
        sMenu += "\n{0}:   {1}".format(iIdx, aType[iIdx-1])

    # obtain the user's choice
    iChoice = misc.get_int(sMenu, iIdx)
    if iChoice == None or iChoice == 0:
        sTxt = ("\n\aInvalid input. Exiting")
        print(sTxt)
        return None

# RE-QUERY THE DATABASE ONLY PICKING UP ON THE CATEGORY SELECTED
    xParam = {"type":aType[iChoice-1]}
    xRestr = {"_id":0, "name":1}
    dGroup = cWorkplace.find(xParam, xRestr)

    # Copy out the data from the database.
    aInd_name = []
    for dQuery in dGroup:
        aInd_name.append(dQuery["name"])

    # Show a menu with the industry names ("Rice Farm" for example)
    iIdx = 0
    sMenu = "\nPlease select the workplace:"
    for choice in aInd_name:
        iIdx += 1
        sMenu += "\n{0}:   {1}".format(iIdx, aInd_name[iIdx-1])

    # obtain the user's choice
    iChoice = misc.get_int(sMenu, iIdx)
    if iChoice == None or iChoice == 0:
        sTxt = ("\n\aInvalid input. Exiting")
        print(sTxt)
        return None

# RE-QUERY THE DATABASE ONLY PICKING UP ON THE CATEGORY SELECTED
    xParam = {"name":aInd_name[iChoice-1]}
    xRestr = {"_id":0}
    dWorkplace = cWorkplace.find(xParam, xRestr)

    # Copy out the data from the database.
    dWkp = {}
    for dQuery in dWorkplace:
        dWkp = dQuery    # Allow us the option for additional queries

# START TO PROCESS
    # NAME THE WORKPLACE
    sFarm_name_combo = ""
    if dWkp["default"] != "" or dWkp["default"] != None:
        # Offer the option to use the default name
        sTxt = ("\nDo you want to use the default name of '{0}' for the {1}?")
        sTxt = sTxt.format(dWkp["default"], dWkp["name"])
        sYn_wkp_name = misc.get_binary(sTxt)
        if sYn_wkp_name == None:
            print("\n\aInvalid input. EXITING")
            return None
        if sYn_wkp_name == "Y":
            sFarm_name_combo = dWkp["default"]

    # Name the workplace / farm.
    if sFarm_name_combo == "":
        # Not yet named.
        sTxt = ("\nEnter the name in the Latin alphabet (accents allowed) of " +
            "the workplace")
        print(sTxt)
        sFarm_name_lat = input()

        sTxt = ("\nEnter the name in the Other alphabet (UTF-8 encoding) of " +
            "the workplace")
        print(sTxt)
        sFarm_name_cyr = input()

        # Combine int 'sFarm_name_combo'
        if sFarm_name_cyr == "" or sFarm_name_cyr == None:
            sFarm_name_combo = "{0}".format(sFarm_name_lat)
        else:
            sFarm_name_combo = "{0}/{1}".format(sFarm_name_lat, sFarm_name_cyr)

    # EXACT FOOTPRINT:
    sTxt = ("Is the exact footprint known? " +
            "(Taken directly from the map as sq.mm).")
    sExact_footprint = misc.get_binary(sTxt)
    if sExact_footprint == None:
        print("\n\aInvalid input. EXITING")
        return None

    # APPROXIMATE FOOTPRINT:
    if sExact_footprint == "N":
        # Confirm information
        sTown_lat = dGeo_element["aName"]["lat"]
        fArea_val = dGeo_element["aArea"]["qty"]
        sArea_units = dGeo_element["aArea"]["uom"]
        sFarm_descr = dWkp["name"]

        # Request the input of the area for the element
        sTxt = ("{0} has an area of {1}{2}. What ratio (0.01 to 0.99) is " +
                "{3} ('{4}')?")
        sTxt = sTxt.format(sTown_lat, fArea_val, sArea_units, sFarm_descr,
                sFarm_name_combo)
        fFarm_percent = misc.get_float(sTxt, 1.00)
        if fFarm_percent == None:
            sTxt = ("\n\aInvalid input. EXITING")
            print(sTxt)
            return None

        # Calculate the footprint
        fFarm_footprint = fFarm_percent * fArea_val
        fFarm_footprint = round(fFarm_footprint, 3)
        dFarm_footprint = {"val":fFarm_footprint, "uom":sArea_units}
    # EXACT FOOTPRINT IS KNOWN:
    else:
        # Confirm information
        sTown_lat = dGeo_element["aName"]["lat"]
        fMap_a = dGeo_element["aMap"]["a"]
        fMap_scale = dGeo_element["aMap"]["fScale"]
        sFarm_descr = dWkp["name"]

        # Get the area from the user
        sTxt = ("{0} has a mapped area of {1}sq.mm. What is the mapped area" +
            " of {2} in sq.mm?")
        sTxt = sTxt.format(sTown_lat, fMap_a, sFarm_name_combo)
        fSq_mm_farm = misc.get_float(sTxt, fMap_a)

        # Check that we passed the valiation
        if fSq_mm_farm == None: return None

        dFootprint = misc.calc_area(fSq_mm_farm, fMap_scale)
        if dFootprint == None: return None
        dFarm_footprint = {
            "val":dFootprint["qty"],
            "uom":dFootprint["uom"]}

# CALCULATE THE STATISTICS GENERATED BY THE FARM/FACTORY
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# LABOUR:
    # Wkf = Workforce or labour
    fWkf_val = dWkp["aaLabour"]["aMain"]["fRate"]
    sWkf_uom = dWkp["aaLabour"]["aMain"]["units"]   # units of measure
    # Workplace or farm
    fFarm_val = dFarm_footprint["val"]
    sFarm_uom = dFarm_footprint["uom"]

    # Let's get the units onto the same page:
    fTot_main = 0.0            # Result of the final calculation of main workers
    sError = ("\n\aUnits of area are grossly mismatched, and will not be" +
        "converted.\nLabour units are {0}; Workplace is in {1}")
    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    if sWkf_uom == "empl/ha":
        # FARMS, AGRICULTURE
        if sFarm_uom == "sq.m":
            print(sError.format(sWfk_uom, sFarm_uom))
            return None                         # Gross mismatch
        elif sFarm_uom == "ha":
            pass                                # No modification needed
        elif sFarm_uom == "sq.km":
            fFarm_val = fFarm_val * 100         # convert to ha
        else:
            print("\n\aInvalid unit of measure for 'farm'. EXITING")
        fTot_main = fFarm_val * fWkf_val

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "empl/sq.km":
        # CATTLE RANCH.
        if sFarm_uom == "sq.m":
            print(sError.format(sWfk_uom, sFarm_uom))
            return None                         # Gross mismatch
        elif sFarm_uom == "ha":
            fFarm_val = fFarm_val / 100         # Convert to sq.km
        elif sFarm_uom == "sq.km":
            pass                                # No modification needed
        else:
            print("\n\aInvalid unit of measure for 'farm'. EXITING")
        fTot_main = fFarm_val * fWkf_val

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "empl":
        # QUARRY, MINE, and other "static" establishments
        sTxt = ("Enter the number of MAIN employees working at {0}")
        sTxt = sTxt.format(sFarm_name_combo)
        fTot_main = misc.get_float(sTxt)
        if fTot_main == None: return

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "sq.m/empl":
        # 1-STOREY OFFICE, FACTORY
        if sFarm_uom == "sq.m":
            fTot_main =  fFarm_val / fWkf_val
        else:
            print(sError.format(sWkf_uom, sFarm_uom))
            return None                             # Gross mismatch

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "sq.m/floor/empl":
        # MULTISTOREY OFFICE BUILDINGS
        if sFarm_uom == "sq.m":
            fTot_main = fWkf_val / fFarm_val
            sTxt = "Enter the number of floors that this building has."
            iStorey_cnt = misc.get_int(sTxt)
            if iStorey_cnt == None: return
            fTot_main = fFarm_val * iStorey_cnt / fWkf_val
        else:
            print(sError.format(sWfk_uom, sFarm_uom))
            return None                          # Gross mismatch

    else:
        print("\n\aInvalid labour unit of measure (uom) detected. EXITING")
        return None

    # These demographics will add-up for this particular factory. They are
    # divided by income level (poor, low, medium, high, rich) and by gender,
    # allowing for combination like 'middle-income female' ('mf'). The number
    # of vehicle number-plates required is also recorded. These are issued to
    # cars, trucks, trailers, motorbikes and trailers.
    aDemogfx = {
        "pm":0, "lm":0, "mm":0, "hm":0, "rm":0,
        "pf":0, "lf":0, "mf":0, "hf":0, "rf":0,
        # Vehicle registration counts are included in here to make it easier
        # to pass it in and out of the routines.
        "veh_reg":0,
    }

    # MAIN DEMOGRAPHIC CALCULATION
    xMain_type = dWkp["aaLabour"]["aMain"]["xType1"].lower()
    iMain_rate = dWkp["aaLabour"]["aMain"]["iRate1"]
    fType = (fTot_main * iMain_rate / 100.0)
    iType = int(round(fType, 0))     # Mind your language! (Don't google 'Ruby')
    aDemogfx[xMain_type] += iType           # Add to the demographics table

    # Calculate the Second demographic
    xMain_type = dWkp["aaLabour"]["aMain"]["xType2"].lower()
    iMain_rate = dWkp["aaLabour"]["aMain"]["iRate2"]
    fType = (fTot_main * iMain_rate / 100.0)
    iType = int(round(fType, 0))     # Mind your language! (Don't google 'Ruby')
    aDemogfx[xMain_type] += iType           # Add to the demographics table

    # Vehicle registration
    fEmpl_per_veh = dWkp["aaLabour"]["aMain"]["fEmpl_per_veh"]
    if fEmpl_per_veh > 0:
        fVeh_cnt = fTot_main / fEmpl_per_veh        # Rough number of vehicles
        iVeh_cnt = int(round(fVeh_cnt, 0))          # Round and integerise
        aDemogfx["veh_reg"] += iVeh_cnt

    # SUPERVISOR
    aBriefcase = {                              # Initiate the briefcase object
        "dLabour_element": dWkp["aaLabour"],
        "fTot_main": fTot_main,
        "aDemogfx": aDemogfx,
        "sWho": "aSupv"
    }
    aDemogfx = qCalc_non_main_staff(aBriefcase)

    # MANAGEMENT
    aBriefcase["aDemogfx"] = aDemogfx           # Update the dynamic element
    aBriefcase["sWho"] = "aMgmt"
    aDemogfx = qCalc_non_main_staff(aBriefcase)

    # SUPPORT STAFF
    aBriefcase["aDemogfx"] = aDemogfx           # Update the dynamic element
    aBriefcase["sWho"] = "aSupt"
    aDemogfx = qCalc_non_main_staff(aBriefcase)

    # STATIC VEHICLES
    aDemogfx["veh_reg"] += dWkp["iStatic_veh"]

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# RESOURCE: (Wheat, straw)
    import random                   # "Harvest" variation between farms.
    lResource = dWkp["lResource"]
    iIdx = 0                        # Wheat Farm 0 is wheat, ...1 is Hay
    for dResource in lResource:
        # Nothing is being produced. This could be a service building.
        if dResource["name"] == "None" and dResource["units"] == "-":
            continue

        # Randomise up-front
        fMin = dResource["fMin_yield"]
        fMax = dResource["fMax_yield"]
        fRnd_harvest = random.uniform(fMin, fMax)   # Random between two floats
        sUnit = dResource["units"]                  # t/ha (Tonne per hectare)

        dFarm_out = None                            # Context breaking
        # Resource like wheat and cattle are dependent on area of the farm
        if sUnit[-3:] == "/ha":
            if dFarm_footprint["uom"] == "sq.m":
                print("\n\aBad measurement units. Expected 'ha', got 'sq.m'" +
                    "EXITING")
                return None

            # Assume the farm is either in ha or sq.km
            fRate = dResource["fRate"]
            fArea = dFarm_footprint["val"]

            fAnnual_output = fRate * fArea * fRnd_harvest     # This many t/ha
            # The calculation assumed that area was in ha. However, if it is
            # in sq.km, then we need to apply a correction. 100ha == 1sq.km
            if dFarm_footprint["uom"] == "sq.km":
                fAnnual_output *= 100
            dFarm_out = {
                "resource": dResource["name"],
                "annual_output": round(fAnnual_output, 2),
                "units": "{0}/yr".format(sUnit[:-3]),
            }
        #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
        # Resource like wood
        elif len(sUnit) > 6 and sUnit[-6:] == "/sq.km":
            if dFarm_footprint["uom"] == "sq.m":
                print("\n\aBad measurement units. Expected 'ha', got 'sq.m'" +
                    "EXITING")
                return None

            # Assume the farm is either in ha or sq.km
            fRate = dResource["fRate"]
            fArea = dFarm_footprint["val"]

            fAnnual_output = fRate * fArea * fRnd_harvest     # This many t/ha
            # The calculation assumed that area was in ha. However, if it is
            # in sq.km, then we need to apply a correction. 100ha == 1sq.km
            if dFarm_footprint["uom"] == "ha":
                fAnnual_output /= 100
            dFarm_out = {
                "resource": dResource["name"],
                "annual_output": round(fAnnual_output, 2),
                "units": "{0}/yr".format(sUnit[:-6]),
            }
        #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
        # Resource like stone or clay, which is per employee.
        elif len(sUnit) > 5 and sUnit[-5:] == "/main":
            # here, the output depends on the number of people employed. This
            # could be digging in the ground, where each person digs out a
            # certain amount of clay from the ground.
            fRate = dResource["fRate"]
            fAnnual_output = fRate * fTot_main * fRnd_harvest  # This many t

            dFarm_out = {
                "resource": dResource["name"],
                "annual_output": round(fAnnual_output, 2),
                "units": "{0}/yr".format(sUnit[:-5]),
            }

        sTxt = "{0} {1}".format(sFarm_name_combo, iIdx)
        iIdx += 1
        dGeo_element["aWarehouse"][sTxt] = dFarm_out
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# ADD DATA TO THE CITY
    # WORKFORCE DEMAND << << << << << << << << << << << << << << << << <<
    dTot_dmd_wkf = dGeo_element["aDemand_workforce"]["total"]
    aFor_iteration = dTot_dmd_wkf.copy()
    dThe_item = {
        "sCode":dWkp["code"],           # So that we can identify industry type
        "sName":sFarm_name_combo
    }

    for sGroup in aFor_iteration:
        dTot_dmd_wkf[sGroup] += aDemogfx[sGroup]            # Total for town
        dThe_item[sGroup] = aDemogfx[sGroup]                # Itemised for farm

    dThe_item["iVeh_cnt"] = aDemogfx["veh_reg"]       # road-legal farm vehicles
    dGeo_element["aDemand_workforce"]["aItemised"].append(dThe_item)

    # VEHICLES << << << << << << << << << << << << << << << << << << << <<
    aVehicles = dGeo_element["aVehicles"]
    if aVehicles == {}:
        # Which factory uses how many vehilces is available in
        # aDemand_workforce.aItemised.iVeh_cnt
        dGeo_element["aVehicles"]["tot_road"] = aDemogfx["veh_reg"]
        dGeo_element["aVehicles"]["aItemised"] = {}
        aItemised = dGeo_element["aVehicles"]["aItemised"]
        aItemised[sFarm_name_combo] = aDemogfx["veh_reg"]
    else:
        aItemised = dGeo_element["aVehicles"]["aItemised"]
        aItemised[sFarm_name_combo] = aDemogfx["veh_reg"]

    # FARM FOOTPRINT << << << << << << << << << << << << << << << << << << << <<
    dGeo_element["aFootprint"][sFarm_name_combo] = dFarm_footprint

# DATABASE UPDATE.
    xParam = {"geo_code":sGeo_code}
    xNew_data = {"$set": {
        "aDemand_workforce": dGeo_element["aDemand_workforce"],
        "aVehicles": dGeo_element["aVehicles"],
        "aFootprint": dGeo_element["aFootprint"],
        "aWarehouse": dGeo_element["aWarehouse"]
    }}

    cDest.update_one(xParam, xNew_data)
    print("\n DATABASE ENTRY UPDATED")

#-------------------------------------------------------------------------------
def add_wkp_auto(dBriefcase):
    """ Adds a workplace to the selected city. However, this addition is done
    semi-automatically. For example, a train station would need some labour.
    This version adds an 'aSupply_workplace' element to the geographic entry.
    NOTE that the warehouses are NOT updated: This feature is intended for
    Train stations, Police stations, Fire Departments, Schools, ...

    dBriefase elements:
        ccTremb             # Data base reference
        sGeo_code           # Host's code
        sInd_code           # Industry code (What are we building?)
        sName_lat           # Name of the building
        sYour_id            # The 'S00-001' of the train station
        aArea               # Footprint of the entity built
        iNo_of_builds       # Summarise 23 pre-schools into one entry.
        lServices           # Geocodes which this facility is used by
        fCapacity           # How much is used
    """
    # Unpack the briefcase
    ccTremb = dBriefcase["ccTremb"]
    sGeo_code = dBriefcase["sGeo_code"]
    sInd_code = dBriefcase["sInd_code"]
    sName_lat = dBriefcase["sName_lat"]
    sYour_id  = dBriefcase["sYour_id"]
    aArea     = dBriefcase["aArea"]                     # Footprint
    iNo_of_builds = dBriefcase["iNo_of_builds"]         # Avoids 23 preschools
    lServices = dBriefcase["lServices"]
    fCapacity = dBriefcase["fCapacity"]               # 22.48 for 23 preschools

    if sGeo_code == None:
        sTxt = ("\nPlease enter the geo-code ('GYG-H' for example) for the" +
                " area you are adding\nworkplaces to.")
        print(sTxt)
        sGeo_code = input().upper()

    # Verify the geo-code and obtain the full element
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None:
        return None

# IMPORT THE INDUSTRY CODE.
    # Find the code in the database
    cWorkplace = db.workplaces_const(ccTremb)
    xParam = {"code":sInd_code}
    xRestr = {"_id":0}
    dWorkplace = cWorkplace.find(xParam, xRestr)

    # Copy out the data from the database.
    dWkp = {}
    iNo_of_hits = 0
    for dQuery in dWorkplace:
        iNo_of_hits += 1
        dWkp = dQuery    # Allow us the option for additional queries

    if iNo_of_hits != 1:
        sTxt = "\n\aInvalid number of workplace codes. Expected 1 got {0}"
        print(sTxt.format(iNo_of_hits))
        return None
# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# NOTE: Cut and paste from "def add_workplace(ccTremb):"
# LABOUR:
    # Wkf = Workforce or labour
    fWkf_val = dWkp["aaLabour"]["aMain"]["fRate"]
    sWkf_uom = dWkp["aaLabour"]["aMain"]["units"]   # units of measure
    # Workplace or farm
    fFarm_val = aArea["val"]
    sFarm_uom = aArea["uom"]

    # Let's get the units onto the same page:
    fTot_main = 0.0            # Result of the final calculation of main workers
    sError = ("\n\aUnits of area are grossly mismatched, and will not be" +
        "converted.\nLabour units are {0}; Workplace is in {1}")
    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    if sWkf_uom == "empl/ha":
        # FARMS, AGRICULTURE
        if sFarm_uom == "sq.m":
            print(sError.format(sWfk_uom, sFarm_uom))
            return None                         # Gross mismatch
        elif sFarm_uom == "ha":
            pass                                # No modification needed
        elif sFarm_uom == "sq.km":
            fFarm_val = fFarm_val * 100         # convert to ha
        else:
            print("\n\aInvalid unit of measure for 'farm'. EXITING")
        fTot_main = fFarm_val * fWkf_val

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "empl/sq.km":
        # CATTLE RANCH.
        if sFarm_uom == "sq.m":
            print(sError.format(sWfk_uom, sFarm_uom))
            return None                         # Gross mismatch
        elif sFarm_uom == "ha":
            fFarm_val = fFarm_val / 100         # Convert to sq.km
        elif sFarm_uom == "sq.km":
            pass                                # No modification needed
        else:
            print("\n\aInvalid unit of measure for 'farm'. EXITING")
        fTot_main = fFarm_val * fWkf_val

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "empl":
        # QUARRY, MINE, and other "static" establishments
        sTxt = ("Enter the number of MAIN employees working at {0}")
        sTxt = sTxt.format(sName_lat)
        fTot_main = misc.get_float(sTxt)
        if fTot_main == None: return

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "sq.m/empl":
        # 1-STOREY OFFICE, FACTORY
        if sFarm_uom == "sq.m":
            fTot_main =  fFarm_val / fWkf_val
        else:
            print(sError.format(sWkf_uom, sFarm_uom))
            return None                             # Gross mismatch

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "sq.m/floor/empl":
        # MULTISTOREY OFFICE BUILDINGS
        if sFarm_uom == "sq.m":
            fTot_main = fWkf_val / fFarm_val
            sTxt = "Enter the number of floors that this building has."
            iStorey_cnt = misc.get_int(sTxt)
            if iStorey_cnt == None: return
            fTot_main = fFarm_val * iStorey_cnt / fWkf_val
        else:
            print(sError.format(sWfk_uom, sFarm_uom))
            return None                          # Gross mismatch

    else:
        print("\n\aInvalid labour unit of measure (uom) detected. EXITING")
        return None

    # These demographics will add-up for this particular factory. They are
    # divided by income level (poor, low, medium, high, rich) and by gender,
    # allowing for combination like 'middle-income female' ('mf'). The number
    # of vehicle number-plates required is also recorded. These are issued to
    # cars, trucks, trailers, motorbikes and trailers.
    aDemogfx = {
        "pm":0, "lm":0, "mm":0, "hm":0, "rm":0,
        "pf":0, "lf":0, "mf":0, "hf":0, "rf":0,
        # Vehicle registration counts are included in here to make it easier
        # to pass it in and out of the routines.
        "veh_reg":0,
    }

    # MAIN DEMOGRAPHIC CALCULATION
    xMain_type = dWkp["aaLabour"]["aMain"]["xType1"].lower()
    iMain_rate = dWkp["aaLabour"]["aMain"]["iRate1"]
    fType = (fTot_main * iMain_rate / 100.0)
    iType = int(round(fType, 0))     # Mind your language! (Don't google 'Ruby')
    aDemogfx[xMain_type] += iType           # Add to the demographics table

    # Calculate the Second demographic
    xMain_type = dWkp["aaLabour"]["aMain"]["xType2"].lower()
    iMain_rate = dWkp["aaLabour"]["aMain"]["iRate2"]
    fType = (fTot_main * iMain_rate / 100.0)
    iType = int(round(fType, 0))     # Mind your language! (Don't google 'Ruby')
    aDemogfx[xMain_type] += iType           # Add to the demographics table

    # Vehicle registration
    fEmpl_per_veh = dWkp["aaLabour"]["aMain"]["fEmpl_per_veh"]
    if fEmpl_per_veh > 0:
        fVeh_cnt = fTot_main / fEmpl_per_veh        # Rough number of vehicles
        iVeh_cnt = int(round(fVeh_cnt, 0))          # Round and integerise
        aDemogfx["veh_reg"] += iVeh_cnt

    # SUPERVISOR
    aBriefcase = {                              # Initiate the briefcase object
        "dLabour_element": dWkp["aaLabour"],
        "fTot_main": fTot_main,
        "aDemogfx": aDemogfx,
        "sWho": "aSupv"
    }
    aDemogfx = qCalc_non_main_staff(aBriefcase)

    # MANAGEMENT
    aBriefcase["aDemogfx"] = aDemogfx           # Update the dynamic element
    aBriefcase["sWho"] = "aMgmt"
    aDemogfx = qCalc_non_main_staff(aBriefcase)

    # SUPPORT STAFF
    aBriefcase["aDemogfx"] = aDemogfx           # Update the dynamic element
    aBriefcase["sWho"] = "aSupt"
    aDemogfx = qCalc_non_main_staff(aBriefcase)

    # STATIC VEHICLES
    aDemogfx["veh_reg"] += dWkp["iStatic_veh"]
# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# NEW TO THE DATABASE ENTRY:
    # If it doesn't exist, create it!
    if "aSupply_workplace" not in dGeo_element.keys():
        dGeo_element["aSupply_workplace"] = []

    # Create the item which will be stored as a workplace
    dItem = {}
        # Avoids individually naming 23 preschools
    dItem["iCnt"] = iNo_of_builds               # How much are we building
    dItem["sCode"] = sInd_code                  # What are we building

    # Name the facility
    if iNo_of_builds != 1:
        dItem["sName"] = sName_lat
    # This is for the 23 prescools bundled together
    else:
        dItem["sName"] = dWkp["default"]

    # Footprint
    if "qty" in aArea.keys():
        fQty = aArea["qty"]
    elif "val" in aArea.keys():
        fQty = aArea["val"]

    fQty *= iNo_of_builds                       # Get the total build
    if aArea["uom"] == "sq.m":
        fQty = fQty / 10000                     # Convert to hectares
    elif aArea["uom"] == "sq.km":
        print("\n\aNothing should be in square kilometers in the city! EXITING")
        return None

    fQty = round(fQty, 3)               # 10 sq.m resoution
    dFarm_footprint = {"qty": fQty, "uom": "ha"}    # Saved externally
    dItem["lServices"]  = lServices
    dItem["fCapacity"]  = fCapacity

# Save in the array
    dGeo_element["aSupply_workplace"].append(dItem)

#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# ADD DATA TO THE CITY
    # WORKFORCE DEMAND << << << << << << << << << << << << << << << << <<
    dTot_dmd_wkf = dGeo_element["aDemand_workforce"]["total"]
    aFor_iteration = dTot_dmd_wkf.copy()
    dThe_item = {
        "sCode":dWkp["code"],           # So that we can identify industry type
        "sName":sName_lat
    }

    for sGroup in aFor_iteration:
        dTot_dmd_wkf[sGroup] += aDemogfx[sGroup]            # Total for town
        dThe_item[sGroup] = aDemogfx[sGroup]                # Itemised for farm

    dThe_item["iVeh_cnt"] = aDemogfx["veh_reg"]       # road-legal farm vehicles
    dGeo_element["aDemand_workforce"]["aItemised"].append(dThe_item)

    # VEHICLES << << << << << << << << << << << << << << << << << << << <<
    aVehicles = dGeo_element["aVehicles"]
    if aVehicles == {}:
        # Which factory uses how many vehilces is available in
        # aDemand_workforce.aItemised.iVeh_cnt
        dGeo_element["aVehicles"]["tot_road"] = aDemogfx["veh_reg"]
        dGeo_element["aVehicles"]["aItemised"] = {}
        aItemised = dGeo_element["aVehicles"]["aItemised"]
        aItemised[sName_lat] = aDemogfx["veh_reg"]
    else:
        aItemised = dGeo_element["aVehicles"]["aItemised"]
        aItemised[sName_lat] = aDemogfx["veh_reg"]

    # FARM FOOTPRINT << << << << << << << << << << << << << << << << << << << <<
    dGeo_element["aFootprint"][sName_lat] = dFarm_footprint

# DATABASE UPDATE.
    xParam = {"geo_code":sGeo_code}
    xNew_data = {"$set": {
        "aDemand_workforce": dGeo_element["aDemand_workforce"],
        "aVehicles": dGeo_element["aVehicles"],
        "aFootprint": dGeo_element["aFootprint"],
        "aSupply_workplace": dGeo_element["aSupply_workplace"],
    }}

    cDest.update_one(xParam, xNew_data)
    print("\n DATABASE ENTRY UPDATED")
    return True

#-------------------------------------------------------------------------------
# X: REMOVES WORKPLACE FROM TOWN'S REGISTER.
#-------------------------------------------------------------------------------
def remove_workplace(ccTremb):
    """ Gives the option of removing an assigned workplace. If the town has lost
    its iron smelter, use this faciltiy to adjust the database.
    """

    # Get the geocode of the town in question
    sTxt = ("\nPlease enter the geo code ('GYN-G') of the area you want to" +
            " work on")
    print(sTxt)
    sGeo_code = input().upper()

    # Look-up the geocode
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

    # Ask for the item to be removed.
    sTxt = ("\nEnter the code ('FHI') of the entity you want to remove")
    print(sTxt)
    sItem_code = input().upper()

    # Ask for the name of the item to be removed
    sTxt = ("\nEnter the name ('iron smelter'), in the correct case, of the" +
            " item you want to\nremove")
    print(sTxt)
    sItem_name = input()

    # Verify that the object exists.
    aItemised = dGeo_element["aDemand_workforce"]["aItemised"]
    if len(aItemised) == 0:
        print("\n\aZero items found. Exiting")
        return None

    # Count the number of instances
    iNo_of_hits = 0
    for dItem in aItemised:
        if dItem["sCode"] == sItem_code and dItem["sName"] == sItem_name:
            iNo_of_hits += 1

    # Error out
    if iNo_of_hits != 1:
        print("\n\aMultiple items with same description found. Unwilling to " +
            "remove data.")
        return None

    # Delete the item in the list
    iIdx = 0
    iNo_of_items = len(aItemised)

    # Iterate through the indexes. I don't want to iterate through the list
    # itself, as it is getting modified inside the loop.
    for iIdx in range(iNo_of_items):
        dItem = aItemised[iIdx]
        if dItem["sCode"] == sItem_code and dItem["sName"] == sItem_name:
            del aItemised[iIdx]     # Remove the requested item
            break

    # ----------------
    # Sort out the vehicles
    dGeo_element["aVehicles"]["aItemised"].pop(sItem_name)

    # Sort out the footprint
    dGeo_element["aFootprint"].pop(sItem_name)

    # Sort out the warehouse
    dWarehouse = dGeo_element["aWarehouse"]
    for iCnt in range(4):      # Lets assume that there could be 4 products made
        sKey = "{0} {1}".format(sItem_name, iCnt)
        if sKey in dWarehouse.keys():
            dWarehouse.pop(sKey)

    # All done.
# DATABASE UPDATE.
    xParam = {"geo_code":sGeo_code}
    xNew_data = {"$set": {
        "aDemand_workforce": dGeo_element["aDemand_workforce"],
        "aVehicles": dGeo_element["aVehicles"],
        "aFootprint": dGeo_element["aFootprint"],
    }}

    cDest.update_one(xParam, xNew_data)
    print("\n DATABASE ENTRY UPDATED")
    return True


#-------------------------------------------------------------------------------
# SUB-MENU
#-------------------------------------------------------------------------------
def sub_menu():
    """ Provides choices for the land mapped in CAD """

    ccTremb = db.connect()
    cDest = db.destinations(ccTremb)
    sSub_menu = """

DESTINATIONS SUB-MENU (D):
.:  Exit
1:  Add an area
2:  View 'children'
3:  View single element
4:  Pretty print a single element to a file

B:  Balance town: add demographic for policemen, firefighters, teachers...
E:  Edit an entry
G:  Assign geo-codes to 'children'. (Use once a parent has all its children)
M:  Add a map
U:  Update parent with children's data (demographics, vehilces, resources)
W:  Add workplace: generates population demand in town.
X:  Remove workplace: Can be used to fix 'mistakes'
""" # Closes the multi=line txt

    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

    # User has made their choice. Now, process it.
        if sInput == ".":           # Exit
            bExit = True
        elif sInput == "1":         # New
            add_area_to_db(ccTremb)
        elif sInput == "2":         # View children
            view_children(ccTremb)
        elif sInput == "3":         # Outputs all the data for one geo-code
            view_single(ccTremb)
        elif sInput == "4":         # Pretty print single element
            pretty_print_single(ccTremb)
        elif sInput == "B":         # Population-dependant workforce was added
            balance_town(ccTremb)
        elif sInput == "E":         # Edit an entry
            edit_entry(ccTremb)
        elif sInput == "G":         # Assign geocodes to all children
            assign_geocodes(ccTremb)
        elif sInput == "M":         # Add a map for referencing
            add_map_to_db(ccTremb)
        elif sInput == "U":         # Update parent with children's data
            update_parent(ccTremb)
        elif sInput == "W":         # Add workplaces (farms, offices)
            add_workplace(ccTremb)
        elif sInput == "X":         # Remove worplace
            remove_workplace(ccTremb)
