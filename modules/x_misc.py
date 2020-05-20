""" Miscellaneous helper routines """
def base_conv(integer, chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """ Converts an integer a base. The function accepts the character map used
    in the conversion. The default setting is base36. """

    if integer < 0:
        # Only interested in positive numbers
        integer = abs(integer)
    if integer == 0:
        return chars[0]

    # "Calculate" the converted value, starting at the least significant element
    result = ""
    while integer > 0:
        integer, remainder = divmod(integer, len(chars))
        result = chars[remainder] + result
    return result

#-------------------------------------------------------------------------------
def clean_my_id(sDirty):
    """ Converts 'D00-00A' to '0000A'. Effectively removes the dash and the
     first character"""
    sDirty = sDirty[1:]                                # Removes the initial "D"
    sClean = sDirty.replace("-", "")                           # Remove the dash
    return(sClean)

#-------------------------------------------------------------------------------
def get_float(sTitle, fTop_lim = None, bNeg = False):
    """ Prints the sTitle on the screen, then the user is propted for an input.
    The input is tested for being numeric. Afterwards, it is tested for the
    specified limit. The 'bNeg' flag true means that the input may be negative
    """
    sTxt = "\n{0}"                      # Import question: prepend with linefeed
    print(sTxt.format(sTitle))
    sInput = input()

    # Case where "its easier to ask for forgiveness than permission"
    try:
        fInput = float(sInput)
    except ValueError:
        print("\n\aInput needs to be a floating-point number")
        return None

    # We got our float converted. Now do its compares.
    if (fTop_lim != None) and (fInput > fTop_lim):
        sTxt = "\n\aTop limit has been exceeded. Input: {0}; Lim: {1}"
        print(sTxt.format(fInput, fTop_lim))
        return None

    # Check if negative input is allowed.
    if (bNeg == False) and (fInput < 0.0):
        print("\n\aInput is negative, which is not allowed")
        return None

    return fInput

#-------------------------------------------------------------------------------
def get_int(sTitle, iTop_lim = None, bNeg = False):
    """ Prints the sTitle on the screen, then the user is propted for an input.
    The input is tested for being integer. Afterwards, it is tested for the
    specified limit. The 'bNeg' flag true means that the input may be negative
    """

    sTxt = "\n{0}"                      # Import question: prepend with linefeed
    print(sTxt.format(sTitle))
    sInput = input()

    # Case where "its easier to ask for forgiveness than permission"
    try:
        iInput = int(sInput)
    except ValueError:
        print("\n\aInput needs to be an integer number")
        return None

    # We got our float converted. Now do its compares.
    if (iTop_lim != None) and (iInput > iTop_lim):
        sTxt = "\n\aTop limit has been exceeded. Input: {0}; Lim: {1}"
        print(sTxt.format(iInput, iTop_lim))
        return None

    if (bNeg == False) and (iInput < 0):
        print("\n\aInput is negative, which is not allowed")
        return None

    return iInput

#-------------------------------------------------------------------------------
def get_binary(sTitle):
    """ Prints the sTitle on the screen, and the instruction to enter Y or N.
    Then the user is propted for an input.
    If the input is not a 'Y', 'y', 'N', 'n' a None is returned. Otherwise, a
    'Y' or 'N' is returned."""

    # Format the question: new line, question itself, new line, options.
    sTxt = "\n{0}\nEnter 'y'/'1' or 'n'/'0' (case insensitive)\n"
    print(sTxt.format(sTitle))
    sInput = input().upper()

    # Convert the numerics
    if sInput == "1": sInput = "Y"
    if sInput == "0": sInput = "N"
    if (sInput != "Y") and (sInput != "N"):
        print("\n\aInvalid input for binary choice. "+
              "Expected 'Y', 'y', '1', 'N', 'n' or '0'")
        return None

    return sInput

#-------------------------------------------------------------------------------
def get_demo(sTitle):
    """ Prints the title on the screen and accepts the demographic code as input
    Method then validates that the demographic code is correct. The validation
    checks the first character is of the correct income group (P, L, M, R, H)
    and that it is combined with the correct gender (M, F). Method returns a
    'none' if the verification fails."""

    print(sTitle)

    sInput = input().upper()
    # Validate the input received
    bValid = False
    for pop_group in ['P', 'L', 'M', 'H', 'R']:
        if sInput[0] != pop_group: continue

        for pop_gender in ['M', 'F']:
            if sInput[1] != pop_gender: continue
            bValid = True

    # Return validation status
    if bValid == False:
        print("\n\aInvalid input entered")
        return None
    return "{0}".format(sInput[0:2])

#-------------------------------------------------------------------------------
def calc_area(fSq_mm, fScale):
    """ Scales up the area on the map: converts map representation to a area
    'on the ground'. Method returns a dictionary containing the value and the
    area and the units of measure. {'qty':1, 'uom':"sq.km"} for example. These
    units come in three possibilities: 'sq.m', 'ha', 'sq.km'"""

    # No point in converting if we don't have a scale.
    if(fScale == None):
        print("\n\aScale is not defined")
        return None

    # Convert to hectares
    fHa_scale = fScale / 100e3                           # linear mm to sqrt(ha)
    fQty_raw = fSq_mm * fHa_scale**2          # scale up area from map to ground

# Check that it is not too small
    if(fQty_raw < 1):    # Down-grade to sq.m
        fQty_raw *= 100**2                                          # ha in sq.m
        fQty = round(fQty_raw, 0)
        return {"qty":fQty, "uom":"sq.m"}

# Check that it is not too big
    elif(fQty_raw > 100000): # Upgrade to sq.km
        fQty_raw /= 100                                            # ha in sq.km
        fQty = round(fQty_raw, 0)
        return {"qty":fQty, "uom":"sq.km"}

#Publish as is.
    else:
        fQty = round(fQty_raw, 3)
        return {"qty":fQty, "uom":"ha"}

#-------------------------------------------------------------------------------
def find_highest_id(dId_query):
    """ Goes through all the database entries looking for the highest base-36
    identifier. The 'my_id' tag is cleaned and then converted to a decimal
    value prior to being 'judged'
    """

    iHighest = 0
    aEvery_id = []
    for dCode in dId_query:
        aEvery_id.append(dCode["my_id"])
        sBase36 = clean_my_id(dCode["my_id"])        # 'D00-02V' -> '0002V'
        iBase10 = int(sBase36, 36)

        # Look for the highest number.
        if iBase10 > iHighest:
            iHighest = iBase10

    if(False):   # Debugging
        sTxt = "\n\nHighest number is {0}(10) < < < (Inner routine)"
        print(sTxt.format(iHighest))

    return iHighest, aEvery_id

#-------------------------------------------------------------------------------
def verify_geo_code(sGeo_code, cDest, bDont_warn=False):
    """ Method makes sure that the geo-code entered exists in the database.
    Returns the names of the entity"""

    # Verify the geo-code
    xParam = {"geo_code":sGeo_code}
    xRestr = {"_id":0, "aName":1}
    dGeo_query = cDest.find(xParam, xRestr)

    # Look at the results of the query
    iNo_of_hits = 0
    aName = {}

    for query in dGeo_query:
        iNo_of_hits += 1
        aName = query["aName"]

    if iNo_of_hits != 1:
        sTxt = "\n\aGeocode ({0}) verification failed. Exiting"
        if bDont_warn == True:
            print(sTxt.format(sGeo_code))
        return None
    return aName

#-------------------------------------------------------------------------------
def get_geo_element(sGeo_code, cDest):
    """ Method makes sure that the geo-code entered exists in the database.
    Returns the whole geographic database entry"""

    # Verify the geo-code
    xParam = {"geo_code":sGeo_code}
    xRestr = {"_id":0}
    dGeo_query = cDest.find(xParam, xRestr)

    # Look at the results of the query
    iNo_of_hits = 0
    dGeo_element = {}

    for query in dGeo_query:
        iNo_of_hits += 1
        dGeo_element = query

    if iNo_of_hits != 1:
        sTxt = "\n\aGeocode verification failed [{0}].".format(sGeo_code)
        sTxt += " EXITING"
        print(sTxt)
        return None
    return dGeo_element

#-------------------------------------------------------------------------------
def get_map_input(ccTremb, sMap = "item"):
    """ Method asks the user to select the map and enter the co-ordinates of the
    object of interest into the database. Common to 'D', 'H', 'S'.
    """
    import modules.x_database as db

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
    print("\nOn which map is this '{0}'?".format(sMap))

    sMenu = "0: No map\n"
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
        print("\n\aInput is not a numeric value. Returning to menu")
        return None

    # Get the details from the dictionary and write them into the destinations
    # entry.
    iInput = int(sInput)
    dMap = {}
    if(iInput == 0):
        dMap["sRegion"] = "No Map"
        dMap["iYear"] = None
        dMap["fScale"] = None
        dMap["x"] = None
        dMap["y"] = None
        dMap["a"] = None
        return True
    elif(iInput > iCnt):
        print("\nChoice out of range. Returning to menu")
        return None
    else:
        iIdx = iInput - 1
        dMap["sRegion"] = dMap_copy[iIdx]["sRegion"]
        dMap["iYear"] = dMap_copy[iIdx]["iYear"]
        dMap["fScale"] = dMap_copy[iIdx]["fScale"]

# Map location: Co-ordinates on the speciied CAD map.
    if(dMap["fScale"] != None):
        # This only works if the map exists.
        sQuestion = "\nEnter the x-coordinate from the map:"
        fX = get_float(sQuestion, None, True)
        if fX == None: return None
        dMap["x"] = fX

        sQuestion = "\nEnter the y-coordinate from the map:"
        fY = get_float(sQuestion, None, True)
        if fY == None: return None
        dMap["y"] = fY

        sQuestion = "\nEnter the area in mm2 from the map{0}:".format(sMap)
        fA = get_float(sQuestion)
        if fA == None: return None
        dMap["a"] = fA

    # Calcluate the area.
        dArea = calc_area(
                dMap["a"],
                dMap["fScale"]
        )
        if dArea == None: return None
        # Compensate for inconsistency
        dArea_2 = {"val": dArea["qty"], "uom": dArea["uom"]}
    # End of map location entry

    dReturn = {
        "dMap":dMap,
        "dArea":dArea_2,
    }
    return dReturn

#-------------------------------------------------------------------------------
def get_the_map(ccTremb):
    import modules.x_database as db
    """
    Method asks the user to select a map, and returns all the credentials for
    that map.
    """
    # Access the maps database
    cMaps = db.maps_db(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dMap_query = cMaps.find(xParam, xRestr)

    # analyse the query
    iNo_of_maps = 0
    dMap_copy = []

    for dMap in dMap_query:
        iNo_of_maps += 1
        dMap_copy.append(dMap)

    print("\nOn which map are you working?")
    sMenu = "0: No map\n"
    iCnt = 0

    # Display all the options for the map
    for one_map in dMap_copy:
        iCnt += 1
        xScale = "{0:,}".format(int(one_map["fScale"]))    # ","@1k ommas every 1000's
        sTxt = "{0}: {1}, {2} 1:{3}\n"
        sMenu += sTxt.format(iCnt, one_map["sRegion"],
                             one_map["iYear"], xScale)
    sMenu += "99:Invalid choice will exit this sub menu"
    print(sMenu)
    sInput = input()

    if sInput.isnumeric() == False:
        # An inbuilt 'abort' system where the user can enter 'x' to exit.
        print("\n\aInput is not a numeric value. Returning to menu")
        return None

    # Get the scale
    iInput = int(sInput)
    fScale = None
    if(iInput == 0):
        print("\n\aA map must be selected. Returning")
        return None
    elif(iInput > iCnt):
        print("\n\aChoice out of range. Returning to menu")
        return None
    else:
        iIdx = iInput - 1
        return dMap_copy[iIdx]

#-------------------------------------------------------------------------------
def write_debug_txt(dData):
    """ Method writes a dictionary to a file for debugging purposes."""
    sFile_path = "Logs/debug.txt"
    eScratch = open(sFile_path, "w", encoding="utf-8")
    sAll = ""
    for item in dData:
        sAll += "{0}\n".format(item)
    eScratch.write(sAll)
    eScratch.close()
    return None

#-------------------------------------------------------------------------------
def get_train(sType, sData, xParam=None):
    """ method stores HARDCODED constants for train parameters here. It returns
    the specified one.
    Possible inputs: ("acc", None), ("dec", None), ("v_max", None),
    ("cruise", speed_limit_in_kmh)
    """
    # NOTE: All the 'manufactures' must guarantee these numbers. These are
    # minimum or maximum depending on the context. Effectively, the train needs
    # to reach these under all conditions.
    if sType == "norm_pax":
        if sData == "acc":      # Acceleration, also up a 2% incline.
            return 1.0          # m/s/s

        elif sData == "dec":    # Deceleration (service braking)
            return 1.0          # m/s/s

        elif sData == "v_max":  # Top speed allowed by this train.
            return 140.0        # km/h

        elif sData == "cruise": # Converts speed-limit to cruise speed.
            if xParam == None:
                print("\n\a'cruise' speed needs to know speed limit")
                return None
            # Verify that xParam will convert to an integer.
            # Case where "its easier to ask for forgiveness than permission"
            try:
                iInput = int(xParam)
            except ValueError:
                print("\n\a'Speed limit' needs to be an integer number")
                return None

            if xParam < 0: # Negative speed limit?
                print("\n\a'Speed limit' can't be negative")

            if xParam <= 40:    # Allow to travel at the limit
                return xParam

            if xParam > 40:
                return xParam - 5   # Cruising speed at 5km/h below limit
    else:
        pass

#-------------------------------------------------------------------------------
def building_name():
    """ Method generates some personal names which can be used in naming of
    buildings. Method returns either the aName array, False if no name was
    chosen or None for error.
    """
    sTxt = ("\nIs this building named?")
    sNamed_yn = get_binary(sTxt)
    if sNamed_yn == None: return None       # Error

    dFinal = {}                                     # Define the prototype
    if sNamed_yn == "Y":
        bExit = False           # Exit the loop after confirming name
        while bExit == False:
            sTxt = ("\nDo you want random name for the building?")
            sRand_name_yn = get_binary(sTxt)
            # Do a soft-exit (break out of the loop on a bad choice)
            if sRand_name_yn == None:
                bExit = True
                continue

            # Manual name entry
            if sRand_name_yn == "N":
                print ("\nPlease enter the name of the building in Latin " +
                       "(Use international Keyboard)")
                dFinal["lat"] = input()

                # User entered name in Cyrillic
                print ("\nНапиш име будынку в Цырполюю. "
                      +"(пшэлаьч клавятурэ рэьчне)")
                dFinal["cyr"] = input()

            # Randomly generated name
            else:
                # Operated by an external routine
                import modules.x_random_names as rnd_name

                # We are storing the random names from the various systems here.
                # Hence, we will build up one set of arrays for the user to
                #choose
                aLat = []
                aCyr = []

            # Male-static:
                iNo_of_combos = 3
                aName = rnd_name.rnd_male_name(iNo_of_combos)
                aSurname = rnd_name.qRnd_static_surname(iNo_of_combos)

                for iIdx in range(iNo_of_combos):
                    sName = aName[iIdx]["lat"]
                    sSurname = aSurname[iIdx]["lat"]
                    aLat.append("{0} {1}".format(sName, sSurname))

                    sName = aName[iIdx]["cyr"]
                    sSurname = aSurname[iIdx]["cyr"]
                    aCyr.append("{0} {1}".format(sName, sSurname))

            # Male-dynamic:
                iNo_of_combos = 3
                aName = rnd_name.rnd_male_name(iNo_of_combos)
                aSurname = rnd_name.qRnd_dynamic_surname(iNo_of_combos)

                for iIdx in range(iNo_of_combos):
                    sName = aName[iIdx]["lat"]
                    sSurname = aSurname[iIdx]["lat"]
                    aLat.append("{0} {1}".format(sName, sSurname))

                    sName = aName[iIdx]["cyr"]
                    sSurname = aSurname[iIdx]["cyr"]
                    aCyr.append("{0} {1}".format(sName, sSurname))

            # Female-static:
                iNo_of_combos = 3
                aName = rnd_name.rnd_female_name(iNo_of_combos)
                aSurname = rnd_name.qRnd_static_surname(iNo_of_combos)

                for iIdx in range(iNo_of_combos):
                    sName = aName[iIdx]["lat"]
                    sSurname = aSurname[iIdx]["lat"]
                    aLat.append("{0} {1}".format(sName, sSurname))

                    sName = aName[iIdx]["cyr"]
                    sSurname = aSurname[iIdx]["cyr"]
                    aCyr.append("{0} {1}".format(sName, sSurname))

            # Female-dynamic:
                iNo_of_combos = 3
                aName = rnd_name.rnd_female_name(iNo_of_combos)
                aSurname = rnd_name.qRnd_dynamic_surname(iNo_of_combos)

                for iIdx in range(iNo_of_combos):
                    sName = aName[iIdx]["lat"]
                    sSurname = aSurname[iIdx]["lat"]
                    aLat.append("{0} {1}".format(sName, sSurname))

                    sName = aName[iIdx]["cyr"]
                    sSurname = aSurname[iIdx]["cyr"]
                    aCyr.append("{0} {1}".format(sName, sSurname))

            # Display the names
                iNo_of_names = len(aLat)
                sChoices = "0: Choose again\n"         # Don't like the options
                iCnt = 1
                for idx in range(0, iNo_of_names):
                    sTxt = "{0}: {1} / {2}\n"
                    sChoices += sTxt.format(iCnt, aLat[idx], aCyr[idx])
                    iCnt += 1

                iChoice = get_int(sChoices, iNo_of_names)
                if iChoice == None: return None                # Invalid choice
                if iChoice == 0: continue                      # Choose again.
                iChoice -= 1

            # Export the final names
                dFinal["lat"] = aLat[iChoice]
                dFinal["cyr"] = aCyr[iChoice]
            # End of randomly generated names

            # Confirm the name choice
            sNew_lat = dFinal["lat"]
            sNew_cyr = dFinal["cyr"]
            sMenu = "Are the names:\n'{0}'\n'{1}' OK?"
            sMenu = sMenu.format(sNew_lat, sNew_cyr)
            sNames_ok_yn = get_binary(sMenu)
            if sNames_ok_yn == "Y": bExit = True
        # of while loop
        return dFinal
    return False        # No name was given
