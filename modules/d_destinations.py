""" This file operates the 'destinations' sub-menu. Effectively, it accounts for
    the land mapped"""

import modules.x_database as db
import modules.x_misc as misc                            # For base36 conversion

#-------------------------------------------------------------------------------
# COMMON ROUTINES
#-------------------------------------------------------------------------------
def qGet_new_area():
    """ Method returns a blank database template for the 'destinations' entry
    """
    dNew_area = {
        "my_id":None,
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
        "aSupply_workforce": {
            "total": {
                "rm": 0, "rf": 0, "hm": 0, "hf": 0, "mm": 0,
                "mf": 0, "lm": 0, "lf": 0, "pm": 0, "pf": 0},
            "aItemised": []},
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
    return dNew_area
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def qGen_my_id(cDest):
    """ Generates the 'my_id' ('D00-001' for example) code for a new database
    entry. """

    # Get a list of all the registered base-36 codes
    xParam = {}
    xRestr = {"_id":0, "my_id":1}
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
    return sNew_id
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def qSelect_type():
    """ Method selects the type of geographical division from a menu """

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
        return {"lat":"World", "cyr":"Свьят", "lvl":"0"}
    elif sInput == "1":
        return {"lat":"Country", "cyr":"Паньстфо", "lvl":"1"}
    elif sInput == "2":
        return {"lat":"Province", "cyr":"Провинцъя", "lvl":"2"}
    elif sInput == "3":
        return {"lat":"District", "cyr":"Повят", "lvl":"3"}
    elif sInput == "4":
        return {"lat":"County", "cyr":"Воевуцтво", "lvl":"4"}
    elif sInput == "5":
        return {"lat":"Municipality", "cyr":"Гмина", "lvl":"5"}
    elif sInput == "6":
        return {"lat":"Section", "cyr":"Чэьсть", "lvl":"6"}
    elif sInput == "7":
        return {"lat":"Suburb", "cyr":"Пшэдщместе", "lvl":"7"}
    elif sInput == "8":
        return {"lat":"Street", "cyr":"Ульица", "lvl":"8"}
    elif sInput == "9":
        return {"lat":"Property", "cyr":"Дзялка", "lvl":"9"}
    else:
        print("Invalid selection. Returning to menu")
        return None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def qSelect_subtype():
    """ Method selects the subtype of geographical division from a menu """

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
        return "General"
    elif sInput == "1":
        return "Nature"
    elif sInput == "2":
        return "Government"
    elif sInput == "3":
        return "Military"
    elif sInput == "4":
        return "Industrial"
    elif sInput == "5":
        return "Agricultural"
    elif sInput == "6":
        return "Transport"
    elif sInput == "7":
        return "Suburb"
    elif sInput == "8":
        return "Commercial District"
    elif sInput == "9":
        return "Town"
    elif sInput == "10":
        return "Settlement"
    else:
        print("\nInvalid selection. Returning to menu")
        return None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def qChoose_name():
    """ Method allows the user to select a name. It returns both the Latin and
    cyrillic names as a tuple."""

    sName_lat = ""
    sName_cyr = ""
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
            sName_lat = input()

            # User entered name in Cyrillic
            print ("\nНапиш име обшару в Цырполю (пшэлаьч клавятурэ рэьчне)")
            sName_cyr = input()

        # Randomly generated name.
        elif sRand_name_yn == "Y":
            # Operated by an external routine
            import modules.x_random_names as rnd_name

            # We are storing the random names from the various systems here.
            # Hence, we will build up one set of arrays for the user to choose
            aLat = []
            aCyr = []

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

            sName_lat = aLat[iChoice]
            sName_cyr = aCyr[iChoice]

        else:
            print("Invalid choice. Exiting")
            return None

    # Confirm the name choice
        sMenu = "Are the names '{0}' / '{1}' OK?".format(sName_lat, sName_cyr)
        sNames_ok_yn = misc.get_binary(sMenu)
        if sNames_ok_yn == "Y": bExit = True

    return sName_lat, sName_cyr

#-------------------------------------------------------------------------------
# 1: ADD A NEW AREA
#-------------------------------------------------------------------------------
def add_area_to_db(ccTremb):
    """ This enters the process of adding a new area record to the database"""
    # Obtain the highest "my_id" code that is registered in the database.
    # NOTE: this is not safe. A destination may have been dropped. This would
    # cause a parent to have a wrong child registered.

    cDest = db.destinations(ccTremb)

# Generate the unique entry identifier, independently from geo-code. It will
# also check that all the child-parent links are intact.
    sNew_id = qGen_my_id(cDest)
    if sNew_id == None: return None

    print("\nNext id is {0}".format(sNew_id))

# START GETTING THE USER TO ENTER THE NEW DATA.
    # Open a blank dictionary, so that the elements are arranged in a certain
    # order.
    dNew_area = qGet_new_area()
    dNew_area["my_id"] = sNew_id

# HARVEST THE DATA FROM THE USER.
    # Look in the database for the last entry
    xParam = {}                     # All items
    xRestr = {"_id":0, "parent":1}
    cDest = db.destinations(ccTremb)
    dId_query = cDest.find(xParam, xRestr).sort("_id",-1)
    sLast_code = dId_query[0]["parent"]

    xParam = {"my_id":sLast_code}
    xRestr = {"_id":0, "geo_code":1, "aName":1}
    dGeo_query = cDest.find(xParam, xRestr).sort("_id",-1)
    sLast_parent = dGeo_query[0]["geo_code"]
    sP_lat = dGeo_query[0]["aName"]["lat"]
    sP_cyr = dGeo_query[0]["aName"]["cyr"]

    # Give the user the option of selecting the last entered geo-code
    sTxt = ("\nThe last entered geo-code of parent was '{0} ({1} / {2})'. " +
            "\nWould you like to use it again?")
    yn_resue = misc.get_binary(sTxt.format(sLast_parent, sP_lat, sP_cyr))
    if yn_resue == "N":
        # Parent (who is above this area in the hierarchy)
        sTxt = ("\nEnter the 'geo_code' of the parent. "
        +" (example 'GYG', or 'i_am_world')")
        print(sTxt)
        sInput = input().upper()
    else:
        sInput = sLast_parent[:]

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
    aType = qSelect_type()
    if aType == None: return None
    dNew_area["aType"] = aType

    sSub_type = qSelect_subtype()
    if sSub_type == None: return None
    dNew_area["sub_type"] = sSub_type

    lNames = qChoose_name()
    if lNames == None: return None
    sNew_lat, sNew_cyr = lNames

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
# 1A: ADD BATCH OF AREAS
#-------------------------------------------------------------------------------
def add_semi_auto(ccTremb):
    """ Adds Municipalites to a County semi-automatically. The usual process
    takes about 3 hours per County. This process attempts to speed things up:
    1.) The user enters the count of objects within the County
    2.) Program opens that many entries in the database
    3.) User chooses names
    4.) User helps with assigning of geo-codes
    5.) User assigns economic output (optional), which is usually the default.
    6.) The capital gets automated
    """
    import pyperclip                    # For cut and paste ops with windows.
    import random                       # For capital city
    bDebug = False

# Instruction
    sTxt = "You are about to add Municipalites to a County in a semi-automatic"
    sTxt += " way.\nPlease assign the economic output to the Municipalites on"
    sTxt += " the map prior to\ncontinuing.\n"
    print(sTxt)

# County code (the 'parent')
    sTxt = "Please enter the COUNTY geocode (VAA) for example:"
    print(sTxt)
    sGeo_code = input().upper()

    # Verify the input
    cDest = db.destinations(ccTremb)
    dGeo_parent = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_parent == None: return None

    # Verify with the user
    sCap_lat = dGeo_parent["aName"]["lat"]
    sCap_cyr = dGeo_parent["aName"]["cyr"]
    sTxt = "Are you updating [{0}] '{1}' / '{2}'?"
    sTxt = sTxt.format(sGeo_code, sCap_lat, sCap_cyr)
    yn_county = misc.get_binary(sTxt)
    if yn_county == None: return None
    if yn_county == "N":
        sTxt = "Aborted by the user. Returning"
        return None

# Check if this is a new operation or we are resuming
    if len(dGeo_parent["aChildren"]) == 0:

    # Number of municipalities
        sTxt = "Please enter the TOTAL number of MUNICIPALITIES, 'RED AREAS', "
        sTxt += "'GREEN AREAS'"
        iNo_of_mun = misc.get_int(sTxt, 36)
        if iNo_of_mun == None: return None
        if iNo_of_mun < 2:
            print("This is for bulk work. For {0} units, please go manual\n\a")
            return None

    # Generate the start of the 'my_id' sequence
        # We have not assigned any children to the parent yet.
        sNew_id = qGen_my_id(cDest)         # Base of the identification
        sId_seq = misc.clean_my_id(sNew_id) # "D00-0ZZ" -> "000ZZ"
        iId_seq_10 = int(sId_seq, 36)       # Automatic conversion

        # Start the list of children
        aChildren = []

    # Open 'blank' destinations with common parent.
        for iMun in range(iNo_of_mun):
            dNew_area = qGet_new_area()         # Blank template

        # Compute 'my_id'
            iThis_id = iId_seq_10 + iMun

            # Convert to base36
            sBase36 = misc.base_conv(iThis_id)
            sBase36_5 = sBase36.rjust(5, "0")
            # "0002W" -> "D00-02W"
            sNew_id = "D{0}-{1}".format(sBase36_5[:2], sBase36_5[2:])

        # Add this identifier to the child list
            aChildren.append(sNew_id)
            dNew_area["my_id"] = sNew_id
            dNew_area["parent"] = dGeo_parent["my_id"]

        # ADD TO DATABASE
            cDest.insert_one(dNew_area)

        # Print a message to show progress
            sTxt = "[{1}/{2}] Generating new entry'{0}'..."
            sTxt = sTxt.format(sNew_id, iMun+1, iNo_of_mun)
            print(sTxt)

    # Add the children to the parent
        xParam = {"my_id":dGeo_parent["my_id"]}
        xNew_data = {"$set":{"aChildren": aChildren}}
        cDest.update_one(xParam, xNew_data)
        print("'Parent' updated")
    else:
        pass

# ASSIGN THE TYPE TO ALL CHILDREN
    # We need to refresh the parent.
    dGeo_parent = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_parent == None: return None
    aChildren = dGeo_parent["aChildren"]

    # Find the first child
    sChild_0 = aChildren[0]                   # All or nothing type of operation
    xParam = {"my_id":sChild_0}
    xRestr = {"_id":0, "aType":1}
    dQuery = cDest.find(xParam, xRestr)

    # See if that child has a type assigned to it already
    bType_done = False
    for query in dQuery:
        if query["aType"]["lat"] != None:
            bType_done = True

    # We need to assign a type to the child
        if bType_done == False:
            aType = qSelect_type()
            if aType == None: return None

            for sChild in aChildren:
                xParam = {"my_id":sChild}
                xRestr = {"_id":0}
                xNew_data = {"$set": {"aType": aType}}
                cDest.update_one(xParam, xNew_data)

# ASSIGN SUB-TYPES
    iNo_of_children = len(aChildren)
    iIdx_child = 0

# Assign the capital (The [0]-child)
    sCapital = aChildren[iIdx_child]

    # See if an assignment already exists
    xParam = {"my_id":sCapital}
    xRestr = {"_id":0, "sub_type":1}
    dQuery = cDest.find(xParam, xRestr)
    bExists = True
    for query in dQuery:
        if query["sub_type"] == None:
            bExists = None

    # Needs to be programmed in.
    if not bExists:
        sTxt = "\nPlease select for the CAPITAL (usually option '0')"
        print(sTxt)

        sSub_type = qSelect_subtype()
        if sSub_type == None: return None

        xParam = {"my_id":sCapital}
        xNew_data = {"$set": {"sub_type": sSub_type}}
        cDest.update_one(xParam, xNew_data)

    iIdx_child += 1            # Point to the next child

# OTHER AREAS
    while iIdx_child < iNo_of_children:
        xParam = {"my_id":aChildren[iIdx_child]}
        xRestr = {"_id":0, "sub_type":1}
        dQuery = cDest.find(xParam, xRestr)
        bExists = True
        for query in dQuery:
            if query["sub_type"] == None:
                bExists = None

        # Child has a type assigned to it.
        if bExists:                 # This child has a type defined
            iIdx_child += 1         # Advance to the next one
            continue

        # Prepare to assign to the child(ren)
        iAreas_left = iNo_of_children - iIdx_child
        sTxt = "There are {0} areas left. ".format(iAreas_left)
        sTxt += "Please choose another category.\n"
        sTxt += "(Choose the unusual ones first, like 'nature' or 'military')"
        print(sTxt)

        sSub_type = qSelect_subtype()
        if sSub_type == None: return None

        # How many areas like that are there?
        sTxt = "How many '{0}' areas are there?".format(sSub_type)
        iArea_cnt = misc.get_int(sTxt, iAreas_left)
        if iArea_cnt == None: return None

        # Update them all
        for iSample in range(iArea_cnt):
            xParam = {"my_id":aChildren[iIdx_child]}
            xNew_data = {"$set": {"sub_type": sSub_type}}
            cDest.update_one(xParam, xNew_data)
            iIdx_child += 1

# ASSIGN NAMES:
    # Capital is first.
    iIdx_child = 0                  # Reset back to the capital

    # See if an assignment already exists
    xParam = {"my_id":aChildren[iIdx_child]}
    xRestr = {"_id":0, "aName":1}
    dQuery = cDest.find(xParam, xRestr)
    bExists = True
    for query in dQuery:
        if query["aName"]["lat"] == None:
            bExists = None

    # Needs to be programmed in.
    if not bExists:
        sTxt = "Do you want to use the name {0} / {1} for the capital?"
        sTxt = sTxt.format(sCap_lat, sCap_cyr)
        yn_reuse = misc.get_binary(sTxt)
        if yn_reuse == None: return
        if yn_reuse == "N":
            lName = qChoose_name()
            if lName == None: return None
            sLat, sCyr = lName
        else:
            sLat = sCap_lat
            sCyr = sCap_cyr

        # 'aName': {'lat': 'Ñoñatça', 'cyr': 'Нёнятя'}
        aName = {"lat":sLat, "cyr":sCyr}
        xParam = {"my_id":aChildren[iIdx_child]}
        xNew_data = {"$set":{"aName":aName}}
        cDest.update_one(xParam, xNew_data)
    iIdx_child += 1

# OTHER AREAS
    while iIdx_child < iNo_of_children:
        xParam = {"my_id":aChildren[iIdx_child]}
        xRestr = {"_id":0, "aName":1, "sub_type":1}
        dQuery = cDest.find(xParam, xRestr)
        bExists = True
        sSub_type = None

    # Check if name exists
        for query in dQuery:
            if query["aName"]["lat"] == None:
                bExists = None
            sSub_type = query["sub_type"]

        if sSub_type == None:
            sTxt = "\n\aAn error has occured: "
            sTxt += "'sub_type' should be already defined. EXITING"
            print(sTxt)
            return

        # Child has a type assigned to it.
        if bExists:                 # This child has a type defined
            iIdx_child += 1         # Advance to the next one
            continue

        # Prepare to assign to the child(ren)
        iAreas_left = iNo_of_children - iIdx_child
        sTxt = "---------\n"
        sTxt += "There are {0} areas left. ".format(iAreas_left)
        sTxt += "Please name a '{0}' area.".format(sSub_type)
        print(sTxt)

        lNames = qChoose_name()
        if lNames == None: return None
        sLat, sCyr = lNames

        aName = {"lat":sLat, "cyr":sCyr}
        xParam = {"my_id":aChildren[iIdx_child]}
        xNew_data = {"$set": {"aName": aName}}
        cDest.update_one(xParam, xNew_data)
        iIdx_child += 1

# ASSIGN GEO-CODES
    print("--------\nGEO-CODE ASSIGNMENT:\n")
    assign_geocodes(ccTremb, sGeo_code)

# GET THE MAP.
    # Check if the children have the map assigned to them already
    xParam = {"my_id":aChildren[0]}             # Check against the capital
    xRestr = {"_id":0, "aMap":1}
    dQuery = cDest.find(xParam, xRestr)

    bMap_done = False
    for query in dQuery:
        if query["aMap"]["sRegion"] != None:
            bMap_done = True

    # Map needs to be assigned
    if bMap_done == False:
        dMap = misc.get_the_map(ccTremb)
        if dMap == None: return None

        for child in aChildren:
            xParam = {"my_id":child}
            xNew_data = {"$set": {
                "aMap.sRegion": dMap["sRegion"],
                "aMap.iYear": dMap["iYear"],
                "aMap.fScale": dMap["fScale"],
                }}
            cDest.update_one(xParam, xNew_data)
        print("Map added to all the children\n")

# GET THE LAND USAGE.
    # Setup a loop without the capital
    print("--------\nLAND USE ASSIGNMENT:\n")
    for child in aChildren[1:]:     # Jump over the capital. It is done last
        # Get the childs sub type
        xParam = {"my_id": child}
        xRestr = {"_id":0}
        dQuery = cDest.find(xParam, xRestr)

        # Run the query on that child
        dChild = []
        for query in dQuery:
            dChild = query

        # Make sure the map exists
        if dChild["aMap"]["fScale"] == None:
            print("\n\aError has occured. Expecting map to be entered. Exiting")
            return None

        # Child already processed
        map_a = dChild["aMap"]["a"]
        if map_a != None:
            continue

        # Select the object to work on.
        iIdx_child = aChildren.index(child) + 1
        sSub_type = dChild["sub_type"]
        sLat = dChild["aName"]["lat"]
        sCyr = dChild["aName"]["cyr"]
        sTxt = "\n[{0}/{1}] Currently working on '{2}' area, named '{3}'/'{4}':"
        sTxt = sTxt.format(iIdx_child, iNo_of_children, sSub_type, sLat, sCyr)
        print(sTxt)

        # x-coord
        sTxt = "Please enter the x-coordinate from the map:"
        fX = misc.get_float(sTxt, None, True)
        if fX == None: return None

        # y-coord
        sTxt = "Please enter the y-coordinate from the map:"
        fY = misc.get_float(sTxt, None, True)
        if fY == None: return None

        # Area
        sTxt = "Please enter the area in sq.mm from the map:"
        fA = misc.get_float(sTxt)
        if fA == None: return None

        # Convert the area.
        dDb_area = misc.calc_area(fA, dChild["aMap"]["fScale"])
        if dDb_area == None: return None

        # Save this data.
        xParam = {"my_id": child}
        xNew_data = {"$set": {
            "aMap.x": fX,
            "aMap.y": fY,
            "aMap.a": fA,
            "aArea": dDb_area
            }}
        cDest.update_one(xParam, xNew_data)

        # How many work-places are there?
        sTxt = "Please enter number of workplaces in the '{0}' area:"
        sTxt = sTxt.format(sSub_type)
        iNo_of_hits = misc.get_int(sTxt)
        if iNo_of_hits == None: return None

        sGeo_code = dChild["geo_code"]

        # Enter the hits.
        for iHit_cnt in range(iNo_of_hits):
            sTxt = ("Please enter [{0}/{1}] work places (like a wheat farm) " +
                "for the '{2}' area")
            sTxt = sTxt.format(iHit_cnt+1, iNo_of_hits, sSub_type)
            print(sTxt)

            # Add the place to the town in a semi-automatic way. Effectively,
            # the name of the place will be defaulted.
            bResp = add_wkp_county(ccTremb, sGeo_code)
            if bResp == None: return None

        # Present data to the user
        sLat = dChild["aName"]["lat"]
        sCyr = dChild["aName"]["cyr"]
        sAll = "{0} {1} / {2}".format(sGeo_code, sLat, sCyr)

    # return geo-code and names on clip-board.
        sTxt = "------\n"
        sTxt += "Geo-code, Names are available on the clip-board. Use 'CTRL-V'"
        sTxt += "\n-------"
        print(sTxt)
        pyperclip.copy(sAll)

        xDummy = input("Press 'Enter' to continue...")

# BALANCE EACH CHILD
    print("--------\nCHILD BALANCING:\n")
    if not bDebug:
        for child in aChildren[1:]:     # Start for loop from second element
            # Get the childs sub type
            xParam = {"my_id": child}
            xRestr = {"_id":0, "geo_code":1, "aName":1}
            dQuery = cDest.find(xParam, xRestr)

            # Run the query on that child
            dChild = []
            for query in dQuery:
                dChild = query

            # Setup the progress text
            sGeo_code = dChild["geo_code"]
            sLat = dChild["aName"]["lat"]
            sCyr = dChild["aName"]["cyr"]
            sTxt = "Balancing [{0}] {1} / {2}...".format(sGeo_code, sLat, sCyr)
            print(sTxt)

            # Do the balancing itself
            bResp = balance_town(ccTremb, sGeo_code)
            if bResp == None: return None

    # UPDATE THE PARENT:
        sParent_geo = dGeo_parent["geo_code"]
        bResp = update_parent(ccTremb, sParent_geo)
        if bResp == None: return None
    else:
        print("BYPASSED FOR DEVELOPMENT AND DEBUGGING")

# WORK ON THE CAPITAL:
    print("--------\nCOUNTY CAPITAL ASSIGNMENT:\n")
    child = aChildren[0]     # Capital is the first element

    # Get the childs sub type
    xParam = {"my_id": child}
    xRestr = {"_id":0}
    dQuery = cDest.find(xParam, xRestr)

    # Run the query on that child
    dCapital = []
    for query in dQuery:
        dCapital = query

    # Confirmation message:
    sLat = dCapital["aName"]["lat"].upper()
    sCyr = dCapital["aName"]["cyr"].upper()

    sTxt = "You are working on the county capital {0} / {1}"
    sTxt = sTxt.format(sLat, sCyr)
    print(sTxt)

    # Make sure the map exists
    if dCapital["aMap"]["fScale"] == None:
        print("\n\aError has occured. Expecting map to be entered. Exiting")
        return None

    if dCapital["aMap"]["a"] == None:
        # x-coord
        sTxt = "Please enter the x-coordinate from the map:"
        fX = misc.get_float(sTxt, None, True)
        if fX == None: return None

        # y-coord
        sTxt = "Please enter the y-coordinate from the map:"
        fY = misc.get_float(sTxt, None, True)
        if fY == None: return None

        # Area
        sTxt = "Please enter the area in sq.mm from the map:"
        fA = misc.get_float(sTxt)
        if fA == None: return None

        # Convert the area.
        dDb_area = misc.calc_area(fA, dCapital["aMap"]["fScale"])
        if dDb_area == None: return None

        # Save this data.
        xParam = {"my_id": child}
        xNew_data = {"$set": {
            "aMap.x": fX,
            "aMap.y": fY,
            "aMap.a": fA,
            "aArea": dDb_area
            }}
        cDest.update_one(xParam, xNew_data)

# TOURISM LEVEL
    sTxt = "On a scale of 0 to 10, how much TOURIST draw value does the "
    sTxt += "capital posess?\nThis has an effect on hotels, restaurants and "
    sTxt += "miscellaneous shops."
    iTourist_score = misc.get_int(sTxt, 10)

# GET DATA FROM THE COUNTY
    sParent_id = dCapital["parent"]               # The link
    xParam = {"my_id": sParent_id}
    xRestr = {"_id":0}
    dQuery = cDest.find(xParam, xRestr)
    dAll = []
    for query in dQuery:
        dAll = query

# Obtain the base demographic
    aDemogfx = dAll["aDemographics"]
    iTot_pax = aDemogfx["iTOT-PAX"]         # Total population
    if iTot_pax == None:
        print("Error: unable to obtain total population. Exiting\n\a")
        return None
    iTot_pax = int(iTot_pax * 1.1)          # Rough estimate for the capial

    print("County is estimated at: {0:,}".format(iTot_pax))

    # The 'prototype' briefcase for working in the capital.
    dBriefcase = {
        "ccTremb": ccTremb,
        "sGeo_code": dCapital["geo_code"],
        "sWkp_code": None,      # Workplace code like 'AWH' for wheat farm
        "iStatic": None,        # Pre-calculated number of static employees
    }

    # Check if the capital has been done already
    aDemand_workforce = dCapital["aDemand_workforce"]
    aItemised = aDemand_workforce["aItemised"]

    if ((len(aItemised) == 0) or
        (aItemised[0]["sCode"] != "OME" and
        aItemised[0]["sCode"] != "FME")):

        if bDebug: bResp = False
        # OFFICE WORKERS: (1:60 iTot)
        fStatic = iTot_pax / 55.555
        fRnd = random.uniform(0.8, 1.25)        # Range of employees
        fStatic = fStatic * fRnd
        iOme = int(fStatic)
        print("'OME': {0} (Base office workers)".format(iOme))
        dBriefcase["sWkp_code"] = "OME"
        dBriefcase["iStatic"] = iOme
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # INDUSTRY WORKERS: (1:2 of office workers)
        fStatic = iOme / 2.0
        fRnd = random.uniform(0.9, 1.33)        # Range of employees
        fStatic = fStatic * fRnd
        iFme = int(fStatic)
        print("'FME': {0} (Base factory/industry workers)".format(iFme))
        dBriefcase["sWkp_code"] = "FME"
        dBriefcase["iStatic"] = iFme
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # THE INDUSTRIALIST / ENTREPRENEUR: (1:12.5k iTot)
        fStatic = iTot_pax / 12500
        fRnd = random.uniform(0.75, 1.25)        # Range of employees
        fStatic = fStatic * fRnd
        iOer = int(fStatic)
        print("'OER': {0} (The industrialist / entrepreneur)".format(iOer))
        dBriefcase["sWkp_code"] = "OER"
        dBriefcase["iStatic"] = iOer
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # THE BANK: (1:2.0k iTot)
        fStatic = iTot_pax / 2000
        fRnd = random.uniform(0.90, 1.11)        # Range of employees
        fStatic = fStatic * fRnd
        iObk = int(fStatic)
        print("'OBK': {0} (The Bank)".format(iObk))
        dBriefcase["sWkp_code"] = "OBK"
        dBriefcase["iStatic"] = iObk
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # MISCELLANEOUS: (1:1000 iTot)
        fStatic = iTot_pax / 1000
        fRnd = random.uniform(0.80, 1.33)        # Range of employees
        fStatic = fStatic * fRnd
        iOxx = int(fStatic)
        print("'OXX': {0} (Misc incl. charities, taxis)".format(iOxx))
        dBriefcase["sWkp_code"] = "OXX"
        dBriefcase["iStatic"] = iOxx
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # COUNTY GOVERNMENT: (1:1000 iTot)
        fStatic = iTot_pax / 1000
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        i4yg = int(fStatic)
        print("'4YG': {0} (County government)".format(i4yg))
        dBriefcase["sWkp_code"] = "4YG"
        dBriefcase["iStatic"] = i4yg
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # DISTRICT GOVERNMENT: (1:10k iTot)
        fStatic = iTot_pax / 10000
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        i3yg = int(fStatic)
        print("'3YG': {0} (District government)".format(i3yg))
        dBriefcase["sWkp_code"] = "3YG"
        dBriefcase["iStatic"] = i3yg
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # MISC SHOPS: (1:240 iTot)
        fStatic = iTot_pax / 240
        fTourist = (iTourist_score / 10)         # 0.0 TO 1.0
        fTourist = fTourist + 1                  # 1.0 to 2.0
        fTourist = fTourist ** 2                 # 1.0 to 4.0
        fStatic = fStatic * fTourist             # Multiply by the factor
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        iRxm = int(fStatic)
        print("'RXM': {0} (Misc shops which also cater to tourists)".format(iRxm))
        dBriefcase["sWkp_code"] = "RXM"
        dBriefcase["iStatic"] = iRxm
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # HOTELS: (1:5k iTot)
        fStatic = iTot_pax / 5000                # Standard count
        fTourist = (iTourist_score / 10)         # 0.0 TO 1.0
        fTourist = fTourist + 1                  # 1.0 to 2.0
        fTourist = fTourist ** 2                 # 1.0 to 4.0
        fStatic = fStatic * fTourist             # Multiply by the factor
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        iGht = int(fStatic)
        print("'GHT': {0} (Hotel for both business & tourist travel)".format(iGht))
        dBriefcase["sWkp_code"] = "GHT"
        dBriefcase["iStatic"] = iGht
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # RESTAURANT: (3:4 Hotel)
        fStatic = iGht * 3 / 4                   # Standard count
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        iGrx = int(fStatic)
        print("'GRX': {0} (Restaurants incl. hotel)".format(iGrx))
        dBriefcase["sWkp_code"] = "GRX"
        dBriefcase["iStatic"] = iGrx
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # COUNTY HOSPITAL: (1:5k iTot)
        fStatic = iTot_pax / 2000                # Standard count
        fTourist = float(iTourist_score)         # 0.0 TO 10.0
        fTourist = fTourist + 1                  # 1.0 to 11.0
        fTourist = fTourist ** (1/6)             # 1.0 to 1.49 (Thumb-suck)
        fStatic = fStatic * fTourist             # Multiply by the factor
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        i4yh = int(fStatic)
        print("'4YH': {0} (County hosplital -- also for tourists)".format(i4yh))
        dBriefcase["sWkp_code"] = "4YH"
        dBriefcase["iStatic"] = i4yh
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # AMBULANCE CREWS: (3:4 Doctors)
        fStatic = i4yh * 3 / 4                   # Standard count
        fRnd = random.uniform(0.95, 1.05)        # Range of employees
        fStatic = fStatic * fRnd
        iHam = int(fStatic)
        print("'HAM': {0} (Ambulance crews)".format(iHam))
        dBriefcase["sWkp_code"] = "HAM"
        dBriefcase["iStatic"] = iHam
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

    # EDUCATION AND PRISONS NEED A MORE ACCURATE NUMBER.
        # Do the balancing itself
        if not bDebug:
            bResp = balance_town(ccTremb, dCapital["geo_code"])
        if bResp == None: return None

    # UPDATE THE PARENT:
        sParent_geo = dGeo_parent["geo_code"]
        if not bDebug:
            bResp = update_parent(ccTremb, sParent_geo)
        if bResp == None: return None

    # Refresh the data
        sParent_id = dCapital["parent"]               # The link
        xParam = {"my_id": sParent_id}
        xRestr = {"_id":0}
        dQuery = cDest.find(xParam, xRestr)
        dAll = []
        for query in dQuery:
            dAll = query

    # Obtain the base demographic
        aDemogfx = dAll["aDemographics"]
        if iTot_pax == None:
            print("Error: unable to obtain total population. Exiting\n\a")
            return None

        iEd4_pax = aDemogfx["ED4-PAX"]              # Private / Religious school
        iEd9_pax = aDemogfx["ED9-PAX"]              # Disabled school
        iYxj_pax = aDemogfx["YXJ-PAX"]              # Juvenile prison
        iYxa_pax = aDemogfx["YXA-PAX"]              # Adult prison

        # PRIVATE / RELIGIOUS SCHOOL: (1:15 ~ 1:20)
        fTeachers = random.uniform(15, 20)      #
        fStatic = iEd4_pax / fTeachers          # Standard count
        fSpare = random.uniform(1, 3)           # "spare teachers"
        fStatic = fStatic + fSpare
        iEd4 = int(fStatic)
        fTpC = round(iEd4_pax / iEd4, 1)

        sTxt = "'ED4': {0} Private / Religious teachers for {1} children ({2} T/C)"
        sTxt = sTxt.format(iEd4, iEd4_pax, fTpC)
        print(sTxt)
        dBriefcase["sWkp_code"] = "ED4"
        dBriefcase["iStatic"] = iEd4
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # DISABLED SCHOOL: (1:4 ~ 1:10)
        fTeachers = random.uniform(4, 10)      #
        fStatic = iEd9_pax / fTeachers          # Standard count
        fSpare = random.uniform(1, 3)           # "spare teachers"
        fStatic = fStatic + fSpare
        iEd9 = int(fStatic)
        fTpC = round(iEd9_pax / iEd9, 1)

        sTxt = "'ED9': {0} 'Disabled' teachers for {1} children ({2} T/C)"
        sTxt = sTxt.format(iEd9, iEd9_pax, fTpC)
        print(sTxt)
        dBriefcase["sWkp_code"] = "ED9"
        dBriefcase["iStatic"] = iEd9
        if not bDebug:
            bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # COUNTY PRISON: (1:5k iTot)
        fStatic = float(iYxj_pax + iYxa_pax)     # Juveniles + Adults
        fStatic = fStatic / 5                    # Usually, 5 prisoners per guard
        fTourist = float(iTourist_score)         # 0.0 TO 10.0
        fTourist = fTourist + 1                  # 1.0 to 11.0
        fTourist = fTourist ** (1/8)             # 1.0 to 1.35 (Thumb-suck)
        fStatic = fStatic * fTourist             # Multiply by the factor
        # 70% of total prisoners are in County jail. Rest are higher up
        fStatic = fStatic * 0.7
        fRnd = random.uniform(1.00, 1.10)        # Range of employees
        fStatic = fStatic * fRnd
        i4yx = int(fStatic)

        iTot = round(iYxj_pax + iYxa_pax, 0)
        fGpP = round(iTot / i4yx, 1)            # Guards per prisoner
        sTxt = ("'4YX': {0} County guards for {1} Juveniles, {2} Adults " +
                "({3} Tot). {4} G/P")
        sTxt = sTxt.format(i4yx, iYxj_pax, iYxa_pax, iTot, fGpP)
        print(sTxt)

        dBriefcase["sWkp_code"] = "4YX"
        dBriefcase["iStatic"] = i4yx
    #    bResp = add_wkp_capital(dBriefcase)
        if bResp == None: return None

        # Do the balancing itself
        if not bDebug:
            bResp = balance_town(ccTremb, dChild["geo_code"])
        if bResp == None: return None

    # UPDATE THE PARENT:
        sParent_geo = dGeo_parent["geo_code"]
        if not bDebug:
            bResp = update_parent(ccTremb, sParent_geo)
        if bResp == None: return None

        # Present data to the user
        sGeo = dCapital["geo_code"]
        sLat = dCapital["aName"]["lat"]
        sCyr = dCapital["aName"]["cyr"]
        sAll = "{0} {1} / {2}".format(sGeo, sLat, sCyr)

        # return geo-code and names on clip-board.
        sTxt = "------\n"
        sTxt += "Geo-code, Names are available on the clip-board. Use 'CTRL-V'"
        sTxt += "\n-------"
        print(sTxt)
        pyperclip.copy(sAll)

    else:
        print("Capital already sorted out!")


    xDummy = input("Press 'Enter' to continue...")

# Notes:
    # pyperclip.copy("Export me to Windows clipboard")



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
            # TODO: Revise formatting
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
def pretty_print_single(ccTremb, sGeo_code = None):
    """ Writes most of the elements from the database in a human-readable format
    """
    import datetime

    if sGeo_code == None:
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

# How much housing to build
    aTot_sup = dData["aSupply_hholds"]["total"]
    if "total" in dData["aDemand_hholds"]:
        aTot_dmd = dData["aDemand_hholds"]["total"]
    else:   # Two formats are possible.
        aTot_dmd = dData["aDemand_hholds"]                     # There is no sub-key

    sAll += "\nBuild housing (Demand - Supply):\n"
    # Process the groups within the total
    sTxt = ">   "
    for sGroup in ["r", "h", "m", "l", "p"]:
        iDelta = aTot_dmd[sGroup] - aTot_sup[sGroup]
        sTxt += " {0}: {1:,};".format(sGroup, iDelta)
    sTxt += "\n"
    sAll += sTxt

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
        if sGroup in ["iVeh_cnt", "iParking"]: continue       # Not population.
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
            if sGroup in ["sCode", "sName", "iVeh_cnt", "iParking"]:
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
            sTxt += " tot road veh: {0:,};".format(dItem["iVeh_cnt"])

        # Sometimes offices have parking in the basement
        if "iParking" in dItem.keys():
            sTxt += " parking bays: {0:,};".format(dItem["iParking"])
        sTxt += "\n>\n"
        sAll += sTxt


# SUPPLY OF WORKFORCE:
    sAll += "----------\n"
    sAll += "Workforce Supply: \n"
    dSup_wkf = dData["aSupply_workforce"]

    # Obtain the total
    iTot_wkf = 0                        # Count them up for conveniance
    for sGroup in dSup_wkf["total"]:
        if sGroup == "iVeh_cnt": continue       # Not population.
        iTot_wkf += dSup_wkf["total"][sGroup]

    sTxt = ">   Grand Total: ({0:,})\n>      ".format(iTot_wkf)

    # Do the men on the top line
    for sGroup in ["rm", "hm", "mm", "lm", "pm"]:
        sTxt += " {0}: {1:,};".format(sGroup, dSup_wkf["total"][sGroup])
    sTxt += "\n>      "

    # Do the women on the bottom line
    for sGroup in ["rf",  "hf", "mf", "lf", "pf"]:
        sTxt += " {0}: {1:,};".format(sGroup, dSup_wkf["total"][sGroup])
    sTxt += "\n>\n"
    sAll += sTxt

    # ITEMISED:
    aItemised = dSup_wkf["aItemised"]
    for dItem in aItemised:
        # Get the total for the itemised item.
        iItem_tot = 0                                 # Add up for conveniance
        for sGroup in dItem:
            # Below is a cheap way of doing OR
            if sGroup in ["sCode", "sName", "iVeh_cnt", "iParking"]:
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
    # Access data on how many pre-school units are needed.
        cCity_services = db.city_services_const(ccTremb)
        xParam = {}
        xRestr = {"_id":0}
        dCity_query = cCity_services.find(xParam, xRestr)

        # Copy out the query
        aCity_copy = []
        for dItem in dCity_query:
            aCity_copy.append(dItem)

    # Start publishing the data
        sTxt = ">   TOTAL PEOPLE: {0:,}\n>\n"
        sAll += sTxt.format(dDfx["iTOT-PAX"])

    # Woring married
        sTxt = ">   Married working people (aHHM-PAX):\n>      "
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aHHM-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Retired married
        sTxt = ">   Married retired people (aHHR-PAX):\n>      "
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aHHR-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Working unmarried
        sTxt = ">   Unmarried working people ('bachelors') (aHHB-PAX):\n>      "
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aHHB-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Retired Unmarried
        sTxt = ">   Unmarried retired people ('golden oldies') (aHHO-PAX):"
        sTxt += "\n>      "                 # We exceeded the 80 column limit
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aHHO-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Disabled
        sTxt = ">   Disabled people, not in a nursing home (aHHD-PAX):\n>      "
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aHHD-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Housewifing
        sTxt = ">   Not working: housewife/-husband OR disabled caregiving "
        sTxt += "(aHHX-PAX):\n>      "
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aHHX-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Unemployed
        sTxt = ">   Unemployed: wanting to work but no work available "
        sTxt += "(aUNE-PAX):\n>      "
        iTot = 0
        for sGroup in ["r", "h", "m", "l", "p"]:
            iItem = dDfx["aUNE-PAX"][sGroup]
            iTot += iItem
            sTxt += " {0}: {1:,};".format(sGroup, iItem)
        sTxt += "\n>      (total: {0:,})\n>\n".format(iTot)
        sAll += sTxt

    # Preschoolers
        sTxt = ">   Preschoolers, all groups                 (ED0-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED0-PAX"])

    # Primary schoolers
        sTxt = ">   Primary schoolers, all groups            (ED1-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED1-PAX"])

    # Middle school
        sTxt = ">   Middle schoolers, all groups             (ED2-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED2-PAX"])

    # High school
        sTxt = ">   High schoolers, all groups               (ED3-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED3-PAX"])

    # Private school
        sTxt = ">   Religious or Private schoolers, all grps (ED4-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED4-PAX"])

    # College
        sTxt = ">   College students, all groups             (ED5-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED5-PAX"])

    # Polytechnic
        sTxt = ">   Polytechnic students, all groups         (ED6-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED6-PAX"])

    # University
        sTxt = ">   University students, all groups          (ED7-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED7-PAX"])

    # RFU
        sTxt = ">   --- (empty slot), all groups             (ED8-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED8-PAX"])

    # Disabled
        sTxt = ">   Disabled students, all groups            (ED9-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["ED9-PAX"])

    # Nursing home, rich
        sTxt = ">   Nursing home for the rich, group 'r'     (OAR-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["OAR-PAX"])

    # Nursing home, standard
        sTxt = ">   Old Age Home, all groups                 (OAH-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["OAH-PAX"])

    # Private nurses
        sTxt = ">   Private nurse, all groups                (OAN-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["OAN-PAX"])

    # Youth Prison
        sTxt = ">   Youth prison, all groups                 (YXJ-PAX): {0:,}\n"
        sAll += sTxt.format(dDfx["YXJ-PAX"])

    # Adult prison
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
            if sCode in dDfx["aREL-PAX"]:
                sTxt = ">      {0:<19} ({1}): {2:,}\n"
                sAll += sTxt.format(dRel["adj"], sCode, dDfx["aREL-PAX"][sCode])
            else:       # No religion numbers
                sTxt = ">      {0:<19} ({1}): {2}\n"
                sAll += sTxt.format(dRel["adj"], sCode, "N/A")

    # units required:
        sAll += ">   Units required:\n"
        for dItem in aCity_copy:
            sCode = dItem["code"]               # "5YP"
            sName = dItem["name"]               # "Police"
            sServes = dItem["serves"]           # Population group concerned
            iCapacity = dItem["capacity"]       # Customers per unit
            fUnits_reqd = dDfx[sServes] / iCapacity # Calculate!
            sTxt = ">       |{0:7.2f} for [{1}] {2}\n"
            sAll += sTxt.format(fUnits_reqd, sCode, sName)


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
            if fVal == None:
                sTxt = ">   {0}: {1}{2}\n"
            else:
                sTxt = ">   {0}: {1:,}{2}\n"
            sAll += sTxt.format(sItem, fVal, units)
    else:
        sAll += ">   N/A\n"

# Write to the file
    print("Please see: {0}".format(sFile_path))
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()

    return True

#-------------------------------------------------------------------------------
# B: BALANCE A TOWN: DEMOGRAPHICS BASED ON INDUSTRIAL DEMAND
#-------------------------------------------------------------------------------
def balance_town(ccTremb, sGeo_code = None):
    """ Adds basic services and calculates demographics based on industrial
    demand of the town. Used on small scale maps. The following basic services
    are assinged; they are ASSUMED to be built in the town.
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
    Once they are in, then a 5-iteration loop is entered where the total
    population is recalculated. As the population increases, the
    Population-dependant services are adjusted accordingly
        """

    if sGeo_code == None:
        sTxt = ("\nPlease enter the geo-code ('GYN-G' for example) of "+
            "the area you wish to balance")
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
# C: BALANCE A CITY: DEMOGRAPHICS BASED ON RESIDENTIAL AREAS
#-------------------------------------------------------------------------------
def balance_city(ccTremb):
    """ Adds basic services and calculates demographics based on actual number
    of residential properties in the suburb. Used on large-scale maps. The
    following basic services are assinged; they are DECLARED MANUALLY to be
    built in the town.
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
    Once they are in, then a 5-iteration loop is entered where the total
    population is recalculated. As the population increases, the
    Population-dependant services are adjusted accordingly
        """

    sTxt = ("\nPlease enter the geo-code ('VAA-00Y' for example) of the area" +
    " you wish to\nbalance")
    print(sTxt)
    sGeo_code = input().upper()

# Build the first demographic
    sOut = qHhold_supplies(ccTremb, sGeo_code)
    if sOut == None:
        return None

    print("----\n")
    print("TOT PAX: {0}".format(sOut))
    print("----\n")





#-------------------------------------------------------------------------------
def qHhold_supplies(ccTremb, sGeo_code):
    """ This method does the actual work. It takes in the Household supplies
    numbers and generates the demographics from that. It is used when designing
    cities on large scale (1:50k), where the placement of schools, police,
    clinics, ect is significant.
    """

    import random
    import math

# VERIFY THE GEO-CODE AND EXTRACT THE ELEMENT.
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

# Extract the supply households numbers
    dTot_hhold = dGeo_element["aSupply_hholds"]["total"]

# ACCESS THE DEMOGRAPHICS DATA BASE
    cDemo = db.demogfx_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dDemo_harvest = cDemo.find(xParam, xRestr)

    dDfx_const = {}
    for dQuery in dDemo_harvest:
        for xKey, xVal in dQuery.items():
            dDfx_const[xKey] = xVal    # Copy out the data

# Reset counters
    dDfx_out = qZero_demogfx()
    dTot_sup_wkf = {"rm":0, "rf":0, "hm":0, "hf":0,
        "mm":0, "mf":0, "lm":0, "lf":0, "pm":0, "pf":0}
    iTot_pax = 0                                              # Total population
    iRes_veh = 0                              # Number of number-plates required

# Get the religion going.
    dReligion = {}
    for denomination in dDfx_const["aaReligion"]:
        sCode = denomination["code"]                # Extract the religion code
        dReligion[sCode] = 0                    # Make a zero list of the codes

# Process each demographic individually
    for sIncome in ["r", "h", "m", "l", "p"]:
        iGrp_pax = 0
        if dTot_hhold[sIncome] == 0: continue               # Skip if zero data
        iHhold_cnt = dTot_hhold[sIncome]                    # Household count

        # Married couples (working and retired)
        fRatio_MvsB = dDfx_const["aPartners"][sIncome]
        fMarried = iHhold_cnt * fRatio_MvsB
        iMarried = int(round(fMarried))

        # Bachlelor households
        iBachelor = iHhold_cnt - iMarried

        # Calculate the number of jailed adults
        iCandidates = iMarried + iBachelor
        for x in range(iCandidates):
            # Prison
            fRnd = random.random()
            if fRnd < dDfx_const["prison_rate"]:
                dDfx_out["YXA-PAX"] += 1    # Jailed protagonist

            # Nursing home
            fRnd = random.random()
            if fRnd < dDfx_const["nursing_home_rate"]:
                if sIncome == "r":
                    dDfx_out["OAR-PAX"] += 1    # Rich retirement home
                else:
                    dDfx_out["OAH-PAX"] += 1    # Standard retirement home
        # End of prison and retirement home

        # Split Married couples into working and retired
        iMin_age = dDfx_const["min_work_age"]  # 19
        iMax_age = dDfx_const["max_work_age"]  # 65
        iLife_exp = dDfx_const["life_expect"]  # 80

        # Household "duration": People are in housholds for 80 - 19 = 61 years
        # So, 61 is our 100% range.
        iHhold_duration = iLife_exp - iMin_age  # 61

        # Duration of working is: from 19 to 65: That is 46 years of working
        iWorklife = iMax_age - iMin_age     # 46
        fRatio_WvsR = iWorklife / iHhold_duration    # 46/61 = 0.754

        # Calculate the ratio of working couples
        fWork_couples = fRatio_WvsR * iMarried
        iWork_couples = int(round(fWork_couples, 0))

        # Retired couples
        iRetired_couples = iMarried - iWork_couples

        # Working bachelors.
        fWork_bachelors = fRatio_WvsR * iBachelor
        iWork_bachelors = int(round(fWork_bachelors, 0))
        iRetired_bachelors = iBachelor - iWork_bachelors

# CONVERT HOUSEHOLDS TO PEOPLE:
        fRatio_fret = dDfx_const["fraternal_rate"]        # 1.9 singles / hhold

        # Calculate the people from the couples
        fMarried_pax = iWork_couples * 2.0            # Children will come later
        fRetired_pax = iRetired_couples * 2.0         # Retired people
        fBachelor_pax = iWork_bachelors * fRatio_fret # Unmarried workers
        fGold_old_pax = iRetired_bachelors * fRatio_fret # Unmarried, retired

        # Round off and convert format
        iHhm_pax = int(round(fMarried_pax, 0))
        iHhr_pax = int(round(fRetired_pax, 0))
        iHhb_pax = int(round(fBachelor_pax, 0))
        iHho_pax = int(round(fGold_old_pax, 0))

        # Sort out the demographics
        dDfx_out["aHHM-PAX"][sIncome] += iHhm_pax
        dDfx_out["aHHR-PAX"][sIncome] += iHhr_pax
        dDfx_out["aHHB-PAX"][sIncome] += iHhb_pax
        dDfx_out["aHHO-PAX"][sIncome] += iHho_pax

        # Add up the population
        iGrp_pax += iHhm_pax
        iGrp_pax += iHhr_pax
        iGrp_pax += iHhb_pax
        iGrp_pax += iHho_pax

        # Sort out the workforce demand: The issue is that it is not customised
        # towards the industry: I don't know if the industry is going to be
        # dominated by a single gender. hence, the gender is split equally
        sCode_m = "{0}m".format(sIncome)        # Produces "rm" for rich male
        sCode_f = "{0}f".format(sIncome)        # Produces "pf" for poor female

        # The working married
        iTot = iHhm_pax                         # Easier to cut and paste
        fMale = iTot / 2.0                      # Men from the total population
        iMale = int(round(fMale, 0))            # Round-off and convert
        iFemale = iTot - iMale                  # Bias towards men
        dTot_sup_wkf[sCode_m] += iMale
        dTot_sup_wkf[sCode_f] += iFemale

        # The working bachelors
        iTot = iHhb_pax                         # Easier to cut and paste
        fMale = iTot / 2.0                      # Men from the total population
        iMale = int(round(fMale, 0))            # Round-off and convert
        iFemale = iTot - iMale                  # Bias towards men
        dTot_sup_wkf[sCode_m] += iMale
        dTot_sup_wkf[sCode_f] += iFemale

# ADD NON-WORKING PEOPLE
        fDisabled =     dDfx_const["aDisabled_school"][sIncome]
        fHousewife =    dDfx_const["aHousewife"][sIncome]
        iChild_cnt =    dDfx_const["aChildren"][sIncome]   # ch. per family
        fCollege =      dDfx_const["aCollege"][sIncome]
        fPolytech =     dDfx_const["aPolytech"][sIncome]
        fUniversity =   dDfx_const["aUniversity"][sIncome]
        fPvt_school =   dDfx_const["aSpeciality_school"][sIncome]
        fPreschool =    dDfx_const["preschool_rate"]
        fPrison =       dDfx_const["prison_rate"]
        fNursing_home = dDfx_const["nursing_home_rate"]

# CHILDREN
        for iCouple in range(iMarried):         # Married, non-retired have kids
            # Randomly choose the number of children and their ages. If a child
            # is under 18, they stay with their parents. Otherwise, they are
            # ignored.

            # booleans to make life a bit easier
            bDisabled_child = False
            bHousewife = False

            for iChild in range(iChild_cnt):
                # Hazard a guess of the child's age. The calculation below is
                # means 65 - 18 = 47. The parents are in the range of 18 to 65.
                # This means that the child could be between 0 and 47 years old.
                # The '+2' allows for a scenario where the family did not make
                # a child yet.
                iMax_work_age = dDfx_const["max_work_age"]
                iMin_work_age = dDfx_const["high_max_age"]
                iOffset = 2                     # For a recently married family

                iAge_range = iMax_work_age - iMin_work_age + iOffset
                iRnd_age = random.randrange(iAge_range) # Pick age of child
                iRnd_age -= 2      # compensate for a new family. give them time

            # Disabled child
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

                if iRnd_age < 0:              # Childless scenario
                    fPrison *= 0.00           # Adjust chance of prison with age
                elif iRnd_age <= dDfx_const["infant_max_age"]:
                    bInfant = True
                    fPrison *= 0.00           # Adjust chance of prison with age
                elif iRnd_age <= dDfx_const["toddler_max_age"]:
                    bToddler = True
                    fPrison *= 0.00           # Adjust chance of prison with age
                elif iRnd_age <= dDfx_const["primary_max_age"]:
                    bPrimary = True
                    fPrison *= 0.33           # Adjust chance of prison with age
                elif iRnd_age <= dDfx_const["middle_max_age"]:
                    bMiddle = True
                    fPrison *= 0.66           # Adjust chance of prison with age
                elif iRnd_age <= dDfx_const["high_max_age"]:
                    bHigh = True
                    fPrison *= 1.00           # Adjust chance of prison with age
                elif iRnd_age <= dDfx_const["tertiary_max_age"]:
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

                # CRIMINAL CHILD
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
                        dDfx_out["YXJ-PAX"] += 1    #Juvenile prison
                    else:
                        # Remove child from additional schooling
                        bCollege = False
                        bPolytech = False
                        bUniversity = False
                        dDfx_out["YXA-PAX"] += 1    # Adult prison
                    # end of prison selection
                # end of going to prison

                # Sort out the disabled child
                bSchool = bToddler or bPrimary or bMiddle or bHigh
                if bSchool and bDisabled_child:
                    # Remove child from normal school
                    bToddler = False
                    bPrimary = False
                    bMiddle = False
                    bHigh = False
                    dDfx_out["ED9-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                # School for disabled
                if (bTertiary or bSchool) and bDisabled_child:
                    # Child is less than 25 years old and disabled, hence stays
                    # with parent. However, the tertiary level students can
                    # study further.
                    if sIncome == "r":
                        dDfx_out["OAN-PAX"] += 1
                        iGrp_pax += 1                  # Add to population total

                    else:
                        bHousewife = True
                        dDfx_out["aHHX-PAX"][sIncome] += 1  # Caregiver
                        iGrp_pax += 1                  # Add to population total

                if bTertiary and bDisabled_child:
                    dDfx_out["aHHD-PAX"][sIncome] += 1 # Unempl. disabl. child
                    iGrp_pax += 1                      # Add to population total

            # Students, in order of prestege
                if bUniversity:
                    bPolytech = False
                    bCollege = False
                    dDfx_out["ED7-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                if bPolytech:
                    bCollege = False
                    dDfx_out["ED6-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                if bCollege:
                    dDfx_out["ED5-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

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
                    dDfx_out["ED4-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                    bHigh = False
                    bMiddle = False
                    bPrimary = False
                    bPreschool = False

            # High school:
                if bHigh:
                    dDfx_out["ED3-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                if bMiddle:
                    dDfx_out["ED2-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                if bPrimary:
                    dDfx_out["ED1-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total

                if bToddler and bPreschool:
                    dDfx_out["ED0-PAX"] += 1
                    iGrp_pax += 1                      # Add to population total
                # End of individual child
            # End of children

            # SORT OUT NON-WORKING WIFE:
            fRnd = random.random()
            if fRnd < fPrison:
                dDfx_out["YXA-PAX"] += 1

            # Wife in nursing home:
            fRnd = random.random()
            if fRnd < fNursing_home:
                iGrp_pax += 1
                if sIncome == "r":
                    dDfx_out["OAR-PAX"] += 1
                else:
                    dDfx_out["OAH-PAX"] += 1

            # Housewife by choice
            fRnd = random.random()
            if not bHousewife and fRnd < fHousewife:
                dDfx_out["aUNE-PAX"][sIncome] += 1 # Unemployed cntr
                iGrp_pax += 1
            # End of couples

        iTot_pax += iGrp_pax        # Sort out the totals

        # RELIGION GOES HERE
        for denomination in dDfx_const["aaReligion"]:
            sCode = denomination["code"]            # "3R", "AN", ...
            fRatio = denomination[sIncome]          # Demographic group
            fCongragation = iGrp_pax * fRatio
            iCongragation = int(round(fCongragation, 0))
            dReligion[sCode] += iCongragation       # Add up across demographics

    # VEHICLE COUNTS
        fRet = dDfx_const["aaVehicles"]["retiree_derate"]
        fBac = dDfx_const["aaVehicles"]["bachlelor_derate"]

        # Loop through each of the categories: bicycle, motorbike, car, airplane
        for iCnt in range(4):
        # Select the transport technology
            # Bicycle
            if iCnt == 0:
                fType = dDfx_const["aaVehicles"]["aBicycle"][sIncome]
                sVeh_type = "VEH-BIC"

            # Motorbike
            elif iCnt == 1:
                fType = dDfx_const["aaVehicles"]["aMotorbike"][sIncome]
                sVeh_type = "VEH-MBK"

            # Car
            elif iCnt == 2:
                fType = dDfx_const["aaVehicles"]["aCar"][sIncome]
                sVeh_type = "VEH-CAR"

            # Aircraft
            elif iCnt == 3:
                fType = dDfx_const["aaVehicles"]["aAircraft"][sIncome]
                sVeh_type = "VEH-AIR"

        # MARRIED WORKING HOUSEHOLD
            fFactor = fType
            fNo_of_veh = dDfx_out["aHHM-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dDfx_out[sVeh_type] += iNo_of_veh

        # MARRIED RETIRED HOUSEHOLD
            fFactor = fType * fRet
            fNo_of_veh = dDfx_out["aHHR-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dDfx_out[sVeh_type] += iNo_of_veh

        # BACHELOR WORKING HOUSEHOLD
            fFactor = fType * fBac
            fNo_of_veh = dDfx_out["aHHB-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dDfx_out[sVeh_type] += iNo_of_veh

        # MARRIED RETIRED HOUSEHOLD
            fFactor = fType * fRet * fBac
            fNo_of_veh = dDfx_out["aHHR-PAX"][sIncome] * fFactor
            iNo_of_veh = int(round(fNo_of_veh, 0))
            dDfx_out[sVeh_type] += iNo_of_veh

            if sVeh_type in ["VEH-MBK", "VEH-CAR"]:     # Cheap way of OR-ing
                iRes_veh += dDfx_out[sVeh_type]         # From all groups

    # DEMAND FOR PUBLIC TRANSPORT
#           "BUS-PAX": 0,       # Number of passangers requiring public transport
        # End of the for-loop for vehicle types

    # End of income level
    dDfx_out["aREL-PAX"] = dReligion               # Add everybody's religion in
    aSup_wkf = {
        "total": dTot_sup_wkf,                    # Only totals calc'd here
        "aItemised": []                           # Empty, as this is the 'lead'
    }

    # Add up the vehicles
    aVehicles = dGeo_element["aVehicles"]
    if aVehicles == {}:                           # Empty: not yet defined
        aVehicles = {
            "tot_road":iRes_veh,
            "aItemised":{"residents":iRes_veh}
            }
    else:
        aItemised = aVehicles["aItemised"]
        if "residents" in aItemised.keys():
            # We do have an entry alerady:
            iOld_veh = aItemised["residents"]       # Get the current count
            aVehicles["tot_road"] -= iOld_veh       # Remove old cnt from total
            if aVehicles["tot_road"] < 0:
                print("\n\aError in adjusting vehicle count. EXITING")
                return None
            # All is well: we can overwrite the vehicle count
            aItemised["residents"] = iRes_veh
            aVehicles["tot_road"] += iRes_veh
        else:   # We don't have an entry
            aItemised["residents"] = iRes_veh
            aVehicles["tot_road"] += iRes_veh
    # End of adding the vehicles

# SAVE THE DATA
    dDfx_out["iTOT-PAX"] = iTot_pax               # The overall population

    xParam = {"geo_code": sGeo_code}
    xNew_data = {"$set": {
        "aSupply_workforce": aSup_wkf,
        "aDemographics": dDfx_out,
        "aVehicles": aVehicles,
    }}

    cDest.update_one(xParam, xNew_data)

# SORT OUT THE DEMANDS
    bRet = qServices_demands(ccTremb, sGeo_code)

# ENTER THE FINAL TOTAL COUNT

    print("City balanced in one iteration")
    return iTot_pax
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
def assign_geocodes(ccTremb, sParent=None):
    """ Takes in the parent's geocode. Method then determines which children
    need to be assigned their own geocodes. Both manual and automatic methods
    are available"""

    if sParent == None:
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
def qHhold_demands(ccTremb, sGeo_code, bHhold_only = False):
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

            # Aircraft
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
    if iLen == 0:            # Not yet defined.
        print("\a\nError: limited data. Exiting")
        return None

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
    if bHhold_only:         # 1:50k map generates demand
        xNew_data = {"$set": {
                "aDemand_hholds": dTot_hhold_dmd,
                }}
    else:                   # Full balancing (default)
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
    xResp = qHhold_demands(ccTremb, sGeo_code, True)
    if xResp == None:
        return None

#-------------------------------------------------------------------------------
# H: ADD HOUSING
#-------------------------------------------------------------------------------
def add_housing(ccTremb):
    """ Dummy routine to get the user to use the external function. It is done
    like that as to allow each housing block to be documented in more detail.
    This will allow for easier manipulation (like destruction, densification)
    """
    print("\n\aPlease use the external function")
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
        if len(aItemised) > 0:
            sThis_name = aItemised[-1]["sName"].lower()  # Extract the last item
            if sTarget_name == sThis_name:
                del aItemised[-1]                    # Remove object of interest

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
# T: UPDATE PARENT WITH CHILDREN'S DATA
#-------------------------------------------------------------------------------
def type_summary(ccTremb):
    """ Outputs a summary (and the total) of all the people employed in a
    specific industry. For example, to obtain the total number of office workers
    request data for 'OMB' """

# Enter the geo code for the area in question
    sTxt = ("\nPlease enter the geo-code ('VAA-00A' for example) for the area" +
            " in question")
    print(sTxt)
    sGeo_code = input().upper()
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None:
        return None

# Verify that we have data for workforce demand
    if dGeo_element["aDemand_workforce"] == {}:
        sTxt = ("\n\a'Demand workforce' is empty. Exiting")
        return None

# Geo_code verified: request industry code input
    sTxt = ("\nPlease enter the 'industry' code ('OMB' for example):")
    print(sTxt)
    sInd_input = input().upper()

# Search through the elements.
    aItemised = dGeo_element["aDemand_workforce"]["aItemised"]
    aElements = []
    for dThe_item in aItemised:
        if dThe_item["sCode"] != sInd_input:
            continue
        aElements.append(dThe_item)

# Elements extracted, lets process them.
    if len(aElements) == 0:
        print("\n\aNothing found")
        return False

# Open the text_file
    # Open a text file where a copy of the information will be written to.
    if sGeo_code == "*":
        sFile_name = "world"                    # Exception in naming convention
    else:
        sFile_name = sGeo_code

    # Work out a name of the file
    sFile_path = "Logs/d_{0}_{1}.txt".format(sFile_name, sInd_input)
    eFile_data = open(sFile_path, "w", encoding="utf-8")

    # Write title:
    eFile_data.write(
        "Summary of {0} for {1}\n".format(
            sInd_input, dGeo_element["aName"]["lat"]))

# Process the data
    # Initial conditions
    dTot = {"rm":0, "rf":0, "hm":0, "hf":0, "mm":0, "mf":0,
            "lm":0, "lf":0, "pm":0, "pf":0}
    iTot = 0

    # Calculate the total
    aGroups = ["rm", "rf", "hm", "hf", "mm", "mf", "lm", "lf", "pm", "pf"]
    for dEntry in aElements:
        for sGroup in aGroups:             # to respect the 80-char column limit
            dTot[sGroup] += dEntry[sGroup]             # Add up the demographics
            iTot += dEntry[sGroup]
    sTxt = ("\nTOTALS ({0:,}):\n".format(iTot))

    # Do the men on the top line
    for sGroup in ["rm", "hm", "mm", "lm", "pm"]:
        sTxt += " {0}: {1:,};".format(sGroup, dTot[sGroup])
    sTxt += "\n"

    # Do the women on the bottom line
    for sGroup in ["rf",  "hf", "mf", "lf", "pf"]:
        sTxt += " {0}: {1:,};".format(sGroup, dTot[sGroup])
    sTxt += "\n\n"
    eFile_data.write(sTxt)

# ITEMISED
    eFile_data.write("------------\n")
    for dEntry in aElements:
        iTot = 0
        for sGroup in aGroups:       # Calculate the total
            iTot += dEntry[sGroup]
        sTxt = ("\n{0} ({1:,}):\n")
        sTxt = sTxt.format(dEntry["sName"], iTot)

        # Do the men on the top line
        for sGroup in ["rm", "hm", "mm", "lm", "pm"]:
            sTxt += " {0}: {1:,};".format(sGroup, dEntry[sGroup])
        sTxt += "\n"

        # Do the women on the bottom line
        for sGroup in ["rf",  "hf", "mf", "lf", "pf"]:
            sTxt += " {0}: {1:,};".format(sGroup, dEntry[sGroup])
        sTxt += "\n"
        eFile_data.write(sTxt)
    # Close the file
    eFile_data.close()
    return True

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
    dParent["aSupply_workforce"]["total"] = {
        "rm":0, "hm":0, "mm": 0, "lm":0, "pm":0,
        "rf":0, "hf":0, "mf": 0, "lf":0, "pf":0,
        "iVeh_cnt": 0
    }
    dParent["aSupply_workforce"]["aItemised"] = []

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
        dChd_sup_wkf = dChild["aSupply_workforce"]
        dItem = {}                              # Build for the itemised logging
        dItem["sName"] = sChild_geo

        for sGroup in dChd_sup_wkf["total"]:
            # For the itemised list
            dItem[sGroup] = dChd_sup_wkf["total"][sGroup]   # Transfer individ
            # For the grand-total on the parent:
            dParent["aSupply_workforce"]["total"][sGroup] += dItem[sGroup]

        # Save the itemised list with the parent
        dParent["aSupply_workforce"]["aItemised"].append(dItem)

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
            "aSupply_workforce": dParent["aSupply_workforce"],
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
def update_parent(ccTremb, sParent=None):
    """ Goes through all its children and gathers demographic, vehicular and
    industrial information. It itemises each child within the parent."""

# GEOCODE OF PARENT:
    if sParent == None:     # Allows Option '1A' to interface here.
        sTxt = ("\nPlease enter the geo-code ('GY' for example) of the parent "+
            "which requests data\nfrom its children.")
        print(sTxt)
        sParent = input().upper()               # Allow user to type in any case

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
    return True

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
def qGen_work_demand(dBriefcase):
    """ The method takes in the workplace data selected either manually
    add_worplace() or semi-automatically add_wkp_semi_auto() if doing a whole
    county at once. It processes the given data and writes it correctly to the
    DB.

    'dBriefcase' contains the following elements: {'dGeo_element', 'dWkp',
    'dFarm_footprint', 'sFarm_name_combo', 'iParking', 'cDest', 'iStatic'} """

# Unpack transport container
    dGeo_element = dBriefcase["dGeo_element"]
    dWkp = dBriefcase["dWkp"]
    dFarm_footprint = dBriefcase["dFarm_footprint"]
    sFarm_name_combo = dBriefcase["sFarm_name_combo"]
    iParking = dBriefcase["iParking"]
    cDest = dBriefcase["cDest"]
    iStatic = dBriefcase["iStatic"]

# CALCULATE THE STATISTICS GENERATED BY THE FARM/FACTORY
#-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# LABOUR:
    # Wkf = Workforce or labour
    fWkf_val = dWkp["aaLabour"]["aMain"]["fRate"]
    sWkf_uom = dWkp["aaLabour"]["aMain"]["units"]   # units of measure
    # Workplace or farm
    if "qty" in dFarm_footprint:        # Equivalent to '.has_key()'
        fFarm_val = dFarm_footprint["qty"]
    else:
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
            return None
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
            return None
        fTot_main = fFarm_val * fWkf_val

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "empl":
        # QUARRY, MINE, and other "static" establishments
        if iStatic == None:
            sTxt = ("Enter the number of MAIN employees working at {0}")
            sTxt = sTxt.format(sFarm_name_combo)
            fTot_main = misc.get_float(sTxt)
        else:
            fTot_main = float(iStatic)      # Input fed in automatically
        if fTot_main == None: return

    #-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    elif sWkf_uom == "sq.m/empl":
        # 1-STOREY OFFICE, FACTORY
        if sFarm_uom == "sq.m":
            fTot_main =  fFarm_val / fWkf_val
        elif sFarm_uom == "ha":
            fTot_main = (fFarm_val * 10e3) / fWkf_val
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
    if iParking != None: dThe_item["iParking"] = iParking   # CBD offices
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
        if sFarm_name_combo in aItemised:   # Already exists, so just add.
            # This scenairo occurs when a named building shares functions. It
            # could be an office block with small shops at the base of it.
            aItemised[sFarm_name_combo] += aDemogfx["veh_reg"]
        else:
            aItemised[sFarm_name_combo] = aDemogfx["veh_reg"]
        aVehicles["tot_road"] += aDemogfx["veh_reg"]

    # FARM FOOTPRINT << << << << << << << << << << << << << << << << << << << <<
    dGeo_element["aFootprint"][sFarm_name_combo] = dFarm_footprint

# DATABASE UPDATE.
    xParam = {"geo_code":dGeo_element["geo_code"]}
    xNew_data = {"$set": {
        "aDemand_workforce": dGeo_element["aDemand_workforce"],
        "aVehicles": dGeo_element["aVehicles"],
        "aFootprint": dGeo_element["aFootprint"],
        "aWarehouse": dGeo_element["aWarehouse"]
    }}

    cDest.update_one(xParam, xNew_data)
    return True         # It is called from 'add_semi_auto'

#-------------------------------------------------------------------------------
def add_workplace(ccTremb):
    """ MANUALLY Adds the 'industries' which operate in this area.
    These could be farms, offices, factories. Effectively, this creates demand
    for a workforce.
    """
# GEOCODE
    # Enter the geo code for the area in question
    sTxt = ("\nPlease enter the geo-code ('GYG-H' for example) for the " +
            "area you are adding\nworkplaces to.")
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
    xRestr = {"_id":0, "name":1, "code":1}
    dGroup = cWorkplace.find(xParam, xRestr)

    # Copy out the data from the database.
    aInd_name = []
    aInd_code = []
    for dQuery in dGroup:
        aInd_name.append(dQuery["name"])
        aInd_code.append(dQuery["code"])

    # Show a menu with the industry names ("Rice Farm" for example)
    iIdx = 0
    sMenu = "\nPlease select the workplace:"
    for choice in aInd_name:
        iIdx += 1
        sTxt = "\n{0}:   ({2}) {1}"
        sTxt = sTxt.format(iIdx, aInd_name[iIdx-1], aInd_code[iIdx-1])
        sMenu += sTxt

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

        sTxt = ("\nDo you want to use the default name of '{0}' "+
            "for the {1}?")
        sTxt = sTxt.format(dWkp["default"], dWkp["name"])
        sYn_wkp_name = misc.get_binary(sTxt)
        if sYn_wkp_name == None:
            print("\n\aInvalid input. EXITING")
            return None
        if sYn_wkp_name == "Y":
            sFarm_name_combo = dWkp["default"]

    # Name the workplace / farm. There is no default name available OR the
    # user wants a manual name
    if sFarm_name_combo == "":
        # Not yet named.
        sTxt = ("\nEnter the name in the Latin alphabet (accents allowed) of " +
            "the workplace")
        print(sTxt)
        sFarm_name_lat = input()

        sTxt = ("\nEnter the name in the Other alphabet (UTF-8 encoding) of " +
            "the workplace.\nPress 'enter' to opt out")
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
    iParking = None                                     # For context breaking
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

        # Add optional parking
        sTxt = "Do you want to specify 'parking'?"
        sYn_parking = misc.get_binary(sTxt)
        if sYn_parking == None: return None
        if sYn_parking == "Y":
            # Get the parking input
            sTxt = ("Enter the area of the parking footprint in sq.mm"+
                " from map.")
            fParking_ftp = misc.get_float(sTxt)
            if fParking_ftp == None: return None

            # Calculate the parking area
            aParking_area = misc.calc_area(fParking_ftp, fMap_scale)
            if aParking_area == None: return None

            # We know the real-world scale of the parking.
            # In the real world, a parking bay is 5.5m x 2.5m (13.75sq.m).
            # However, each vehicle needs access to that bay. The above
            # calcuation gives 7.27veh/100sq.m. However, each vehilce needs some
            # space to get to the bay. Hence, I'm using the figure of
            # 6 veh / 100sq.m (600veh/ha)

            # Verify the units of measurement
            if aParking_area["uom"] != "sq.m":
                print("\nUnexpected calculation result for office parking:\n" +
                    "Expected 'sq.m', but got {0}\a".format(
                        aParking_area["uom"]))
                return None
            fSqm_P = aParking_area["qty"]

            print("Parking is: {0}{1}".format(
                aParking_area["qty"], aParking_area["uom"]))

            sTxt = ("On how many levels are cars parked?")
            iFloors = misc.get_int(sTxt)
            if iFloors == None: return None

            if iFloors > 1 and fSqm_P < 90:
                sTxt = ("\n\aInsufficient space for a ramp " +
                    "(1:10 @ h = 3.6m, w = 2.5m). Exiting")
                return None

            if iFloors > 1:
                fSqm_P -= 90    # Take room for the ramp

            fVeh = 6.0 * fSqm_P / 100
            iVeh = int(round(fVeh, 0))      # Round off to whole vehicles

            fVeh = iVeh * iFloors           # We need to round off per floor.
            iVeh = int(round(fVeh, 0))      # Round off to whole vehicles

            iNo_of_buildings = 1            # Short circuit it.
            fVeh = iVeh * iNo_of_buildings  # Parking in each building
            iParking = int(round(fVeh, 0))      # Round off to whole vehicles

            print("Total of {0} cars can be parked here".format(iVeh))
        # End of parking additional
    # End of exact footprint is known

    dBriefcase = {
        "dGeo_element": dGeo_element,
        "dWkp": dWkp,
        "dFarm_footprint": dFarm_footprint,
        "sFarm_name_combo": sFarm_name_combo,
        "iParking": iParking,
        "cDest": cDest,
        "iStatic":None,         # Used by the capital city.
    }
    bRes = qGen_work_demand(dBriefcase)
    if bRes == None:
        return None
    print("\n DATABASE ENTRY UPDATED")
    return True

#-------------------------------------------------------------------------------
def add_wkp_county(ccTremb, sGeo_code):
    """ BATCH ADDITION (1A-MENU): Method follows the process of the standard
    W-menu with a few exceptions. The name of the place is defaulted, and there
    is no entry of the geo-code as it is already supplied.
    """
    # Get the geographic element:
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

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
    xRestr = {"_id":0, "name":1, "code":1}
    dGroup = cWorkplace.find(xParam, xRestr)

    # Copy out the data from the database.
    aInd_name = []
    aInd_code = []
    for dQuery in dGroup:
        aInd_name.append(dQuery["name"])
        aInd_code.append(dQuery["code"])

    # Show a menu with the industry names ("Rice Farm" for example)
    iIdx = 0
    sMenu = "\nPlease select the workplace:"
    for choice in aInd_name:
        iIdx += 1
        sTxt = "\n{0}:   ({2}) {1}"
        sTxt = sTxt.format(iIdx, aInd_name[iIdx-1], aInd_code[iIdx-1])
        sMenu += sTxt

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

# NAME THE WORKPLACE
    sFarm_name_combo = ""
    if dWkp["default"] != "" or dWkp["default"] != None:
        sFarm_name_combo = dWkp["default"]

    # There is no default name available
    if sFarm_name_combo == "":
        # Not yet named.
        sTxt = ("\nEnter the name in the Latin alphabet (accents allowed) of " +
            "the workplace")
        print(sTxt)
        sFarm_name_lat = input()

        sTxt = ("\nEnter the name in the Other alphabet (UTF-8 encoding) of " +
            "the workplace.\nPress 'enter' to opt out")
        print(sTxt)
        sFarm_name_cyr = input()

        # Combine int 'sFarm_name_combo'
        if sFarm_name_cyr == "" or sFarm_name_cyr == None:
            sFarm_name_combo = "{0}".format(sFarm_name_lat)
        else:
            sFarm_name_combo = "{0}/{1}".format(sFarm_name_lat, sFarm_name_cyr)

# THE WORPLACE FOOTPRINT
    # For farms, this forms the basis of the labour.

    # Confirm information
    sTown_lat = dGeo_element["aName"]["lat"]
    fArea_val = dGeo_element["aArea"]["qty"]
    sArea_units = dGeo_element["aArea"]["uom"]
    sFarm_descr = dWkp["name"]

    # Request the input of the area for the element
    sTxt = ("'{0}' has an area of {1}{2}. What ratio (0.01 to 0.99) is " +
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

    dBriefcase = {
        "dGeo_element": dGeo_element,
        "dWkp": dWkp,
        "dFarm_footprint": dFarm_footprint,
        "sFarm_name_combo": sFarm_name_combo,
        "iParking": None,
        "cDest": cDest,
        "iStatic":None,         # For the capital only
    }
    bRes = qGen_work_demand(dBriefcase)
    if bRes == None:
        return None
    print("\n DATABASE ENTRY UPDATED")
    return True

#-------------------------------------------------------------------------------
def add_wkp_capital(dArrival):
    """ 'I KNOW WHAT I WANT': Effectively, I supply the code of the service and
    its static personel count."""
    # Unpack after 'travel'
    ccTremb = dArrival["ccTremb"]
    sGeo_code = dArrival["sGeo_code"]
    sWkp_code = dArrival["sWkp_code"]
    iStatic = dArrival["iStatic"]

    # Get the geographic element:
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

    # Get the workplace database
    cWorkplace = db.workplaces_const(ccTremb)
    xParam = {"code":sWkp_code}
    xRestr = {"_id":0}
    dWorkplace = cWorkplace.find(xParam, xRestr)

    # Get the workplace result
    dWkp = []
    for query in dWorkplace:
        dWkp = query

    dBriefcase = {
        "dGeo_element": dGeo_element,
        "dWkp": dWkp,
        "dFarm_footprint": dGeo_element["aArea"],
        "sFarm_name_combo": dWkp["default"],
        "iParking": None,
        "cDest": cDest,
        "iStatic":iStatic,         # For the capital only
    }

    bRes = qGen_work_demand(dBriefcase)
    if bRes == None:
        return None

    sTxt = "\n DATABASE ENTRY UPDATED for {0} with {1}"
    sTxt = sTxt.format(dWkp["default"], iStatic)
    print(sTxt)
    return True

#-------------------------------------------------------------------------------
def add_wkp_auto(dBriefcase):
    """ STATIONS (S-MENU): Adds a workplace to the selected city. However, this
    addition is done semi-automatically. For example, a train station would
    need some labour. This version adds an 'aSupply_workplace' element to the
    geographic entry. NOTE that the warehouses are NOT updated: This feature is
    intended for Train stations, Police stations, Fire Departments, Schools, ...

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
        # Building can exist: It could house both offices and shops.
        if sName_lat in aItemised:
            aItemised[sName_lat] += aDemogfx["veh_reg"]
        else:
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

    # Remove from the total
    dTotal = dGeo_element["aDemand_workforce"]["total"]
    iVeh_cnt = 0
    for sElement in aItemised:
        if sElement == "iVeh_cnt":
            iVeh_cnt += sElement["iVeh_cnt"] # Multiple units in buinding
        if sElement in ["sCode", "scode", "sName", "iVeh_cnt", "iParking"]:
            continue            # skip over these
        dTotal[sElement] -= aItemised[sElement]     # Subtract from grand total
        if dTotal[sElement] < 0:
            print("\n\aError in removing element from"+
            " 'aDemand_workforce.total'")
            return None
        # End of 'if'
    # End of updating the total

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
    # Remove from total
    dGeo_element["aVehicles"]["tot_road"] -= iVeh_cnt      # Remove from total
    if dGeo_element["aVehicles"]["tot_road"] < 0:
        print("\n\aError in removing vehicles from total count")
        return None

    # Remove from building
    aVeh_Item = dGeo_element["aVehicles"]["aItemised"]
    aVeh_Item[sItem_name] -= iVeh_cnt     # Buildings can contain mulitipe units
    if aVeh_Item[sItem_name] <= 0:
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
# !: REMOVES DEMOGRAPHICS.
#-------------------------------------------------------------------------------
def reset_demographics(ccTremb):
    """ Sets the population element (The "aDemographics" structure) to its
    initial value.
    """

    # Get the geocode of the town in question
    sTxt = ("\nPlease enter the geo code ('GYN-G') of the area you want to" +
            " work on.\nYou will zero the 'aDemographics' element")
    print(sTxt)
    sGeo_code = input().upper()

    # Look-up the geocode
    cDest = db.destinations(ccTremb)
    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return None

    sTxt = ("\nYou are about to delete population data for {0}." +
        "\nDo you want to continue?")
    sTxt = sTxt.format(dGeo_element["aName"]["lat"])
    sYn_reset_demo = misc.get_binary(sTxt)
    if sYn_reset_demo == False: return None
    if sYn_reset_demo == "N": return False

    #This is it: we are reseting
    aDemographics = qZero_demogfx()

    # Also, take out the 'stray' resident vehicles
    aVeh = dGeo_element["aVehicles"]
    if aVeh != {}:
        iRes = aVeh["aItemised"]["residents"]
        aVeh["tot_road"] -= iRes                # Remove the residents vehilces
        del aVeh["aItemised"]["residents"]      # Remove the whole entry

        xNew_data = {"$set": {
            "aDemographics": aDemographics,
            "aVehicles": aVeh,
            }}

    else:
        xNew_data = {"$set": {"aDemographics": aDemographics}}

    xParam = {"geo_code":sGeo_code}

    cDest.update_one(xParam, xNew_data)
    print("\n DEMOGRAPHICS RESET")
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
1A: Add MUNICIPALITIES semi-automatically
2:  View 'children'
3:  View single element
4:  Pretty print a single element to a file

B:  Balance town: Small-scale maps (1:1M) INDUSTRY DRIVEN DEMOGRAPHICS
C:  Balance city: Large-scale maps (1:50k) HOUSEHOLD DRIVEN DEMOGRAPHICS
D:  Balance non-residential: Household demand for commercial/industrial zones.
E:  Edit an entry
G:  Assign geo-codes to 'children'. (Use once a parent has all its children)
H:  Add housing: Adds household supply
M:  Add a map
T:  Types (workforce demand type summary for example 'OMB')
U:  Update parent with children's data (demographics, vehilces, resources)
W:  Add workplace: generates population demand in town.
X:  Remove workplace: Can be used to fix 'mistakes'

!:  Reset demographics to zero.
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
        elif sInput == "1A":        # Semi-Automatic batch area
            add_semi_auto(ccTremb)
        elif sInput == "2":         # View children
            view_children(ccTremb)
        elif sInput == "3":         # Outputs all the data for one geo-code
            view_single(ccTremb)
        elif sInput == "4":         # Pretty print single element
            pretty_print_single(ccTremb)
        # elif sInput == 5:         # Sub-component which has its own entry
        #   add_sub_comp(ccTremb)
        elif sInput == "B":         # Industry driven balancing:
            balance_town(ccTremb)
        elif sInput == "C":         # City balancing: Driven by available houses
            balance_city(ccTremb)
        elif sInput == "D":         # Calculates housing demand for non-res area
            household_demands(ccTremb)
        elif sInput == "E":         # Edit an entry
            edit_entry(ccTremb)
        elif sInput == "G":         # Assign geocodes to all children
            assign_geocodes(ccTremb)
        elif sInput == "H":         # Adds supply households
            add_housing(ccTremb)
        elif sInput == "M":         # Add a map for referencing
            add_map_to_db(ccTremb)
        elif sInput == "T":         # Outputs total of certain employer types.
            type_summary(ccTremb)
        elif sInput == "U":         # Update parent with children's data
            update_parent(ccTremb)
        elif sInput == "W":         # Add workplaces (farms, offices)
            add_workplace(ccTremb)
        elif sInput == "X":         # Remove worplace
            remove_workplace(ccTremb)
        elif sInput == "!":         # Remove demographics
            reset_demographics(ccTremb)
