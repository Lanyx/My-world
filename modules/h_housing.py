""" Housing keeps track of how much housing has been drawn on the map. It is
intended to be used on a 50k (and lower) maps, where each plot of housing is
defined. A database is opened which keeps track of all the housing plots
declared. This will allow for easier modification in the future. The data
provided is intended to be unbalanced. The demand and supply balancing system
will be provided later in time.
"""

import modules.x_database as db
import modules.x_misc as misc
import modules.d_destinations as d_py

#-------------------------------------------------------------------------------
# 1. Add housing
#-------------------------------------------------------------------------------
def add_housing(ccTremb):
    """ Adds details of the housing to the database """

    # Obtain the highest "my_id" code that is registered in the database.
    xParam = {}
    xRestr = {"_id":0, "my_id":1}
    cHousing = db.housing(ccTremb)
    dId_query = cHousing.find(xParam, xRestr)
    iHighest, aEvery_id = misc.find_highest_id(dId_query)

    if(False):   # Debugging
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
    sNew_id = "H{0}-{1}".format(sBase36_5[:2], sBase36_5[2:])
    print("\nNext id is {0}".format(sNew_id))

# START GETTING THE USER TO ENTER THE NEW DATA.
    # Open a blank dictionary, so that the elements are arranged in a certain
    # order.
    dNew_housing = {
        "my_id":sNew_id,
        "host_geo_code":None,
        "aName":{"lat":None, "cyr":None},  # Is the block of flats named?
        "type":None,            # Green(space), Res(idential)
        "sub_type":None,        # house, lin apt, sq apt, x apt, irreg apt,
        "iUnits_per_floor":0,   # How many apartments in the block
        "iNo_of_floors":1,      # How tall is the building
        "iNo_of_buildings":1,   # How many buildings in the 'package'
        "iTot_units":0,         # Total households in this location
        "sDesc":"",             # Description ex: "9x2x1M; 9 = 7+1S+1SP"
        "demographic":"",       # 'r' to 'p'
        "aParking":{
            "iFloors":1,        # How many levels is parking offered on.
            "iVeh":0,           # Vehicles in total
            "map_a":0,          # sq.mm on the map per floor of the parking area.
        },
        "aMap":{
            "sRegion":None,
            "iYear":None,
            "fScale":None,
            "x":None,
            "y":None,
            "a":None
        },
        "aFpt_bldg":{"qty":None, "uom":None},
        "aArea_plot":{"qty":None, "uom":None},
    }

# Automatically obtain the geo-code of the last entry. Chances are that we'd
# like to re-use it.
    xParam = {}
    xRestr = {"_id":0, "host_geo_code":1}
    dId_query = cHousing.find(xParam, xRestr).sort("_id", 1)
    dId_query.sort("_id", -1)

# Pull out the geo-code
    sGeo_code = dId_query[0]["host_geo_code"]
    cDest = db.destinations(ccTremb)
    dGeo_names = misc.verify_geo_code(sGeo_code, cDest)
    if dGeo_names == None: return None  # An error has occured.

    # Names of the settlement.
    sP_lat = dGeo_names["lat"]
    sP_cyr = dGeo_names["cyr"]

    sTxt = "Are you working on {0} ({1} / {2})?"
    sTxt = sTxt.format(sGeo_code, sP_lat, sP_cyr)
    yn_last_host = misc.get_binary(sTxt)
    if yn_last_host == None: return None
    if yn_last_host == "N":
    # HOST
        sTxt = ("\nWho is hosting this residential area OR greenspace?\n" +
                "Please enter host's geo-code.")
        print(sTxt)
        sGeo_code = input().upper()

    dGeo_element = misc.get_geo_element(sGeo_code, cDest)
    if dGeo_element == None: return
    aHost_name = dGeo_element["aName"]

    dNew_housing["host_geo_code"] = sGeo_code
    sTxt = "\nHosted by {0} / {1}".format(aHost_name["lat"], aHost_name["cyr"])
    print(sTxt)

# TYPE
    sMenu = "\n"
    sMenu += "What type area is it?\n"
    sMenu += "0: Greenspace (Park)\n"
    sMenu += "1: Residential\n"

    iType_option = misc.get_int(sMenu, 1)
    if iType_option == None:
        print("\a")
        return None

    if iType_option == 0:
        dNew_housing["type"] = "Green"
    elif iType_option == 1:
        dNew_housing["type"] = "Res"
    else:
        print("\n\aInvalid choice for area type type")
        return

# SUB-TYPE:
    if dNew_housing["type"] == "Res": # Residential:
        sMenu = "\n"
        sMenu += "Type of housing is it?\n"
        sMenu += "0: House: Free-standing building for 1 or 2 households\n"
        sMenu += "1: Apartments, Linear: Straight block of appartments\n"
        sMenu += "2: Apartments, Square: Square-edged Doughnut-shaped bldg\n"
        sMenu += "3: Apartments, Cross: Cross-shaped building\n"
        sMenu += "4: Apartments, Irregular: Irregularly-shaped building\n"
        sMenu += "5: Other: Something rare, or that doesn't fit above descr.\n"

        iType_option = misc.get_int(sMenu, 5)
        if iType_option == None:
            print("\a")
            return None

        if iType_option == 0:
            dNew_housing["sub_type"] = "house"
        elif iType_option == 1:
            dNew_housing["sub_type"] = "lin apt"
        elif iType_option == 2:
            dNew_housing["sub_type"] = "sq apt"
        elif iType_option == 3:
            dNew_housing["sub_type"] = "x apt"
        elif iType_option == 4:
            dNew_housing["sub_type"] = "irrg apt"
        elif iType_option == 5:
            dNew_housing["sub_type"] = "other"
        else:
            print("\n\aInvalid choice for port type")
            return
    # Greenspace was selected
    else:
        dNew_housing["sub_type"] == "N/A"

# MAP REFERENCE
    sMap = "plot"
    dData = misc.get_map_input(ccTremb, sMap)  # Asks for user to input stuff.
    if dData in [None, True]:                  # No map selected
        print("\n\aInvalid entry from the map. Exiting")
        return None

    # Transfer data through.
    dNew_housing["aMap"] = dData["dMap"]
    dNew_housing["aArea_plot"] = dData["dArea"]

# BUILDING SIZE
    if dNew_housing["type"] == "Res" and dNew_housing["sub_type"] != "house":
        sTxt = "\nEnter the footprint of the building in sq.mm from map."
        fBldg_ftp = misc.get_float(sTxt)
        if fBldg_ftp == None: return None

        # Calculate area
        fScale = dNew_housing["aMap"]["fScale"]
        dNew_housing["aFpt_bldg"] = misc.calc_area(fBldg_ftp, fScale)

# OPTIONAL NAME
    aName = misc.building_name()
    if aName == None: return None
    if aName != False:      # False: if a name was not chosen
        dNew_housing["aName"] = aName


# DEMOGRAPHICS:
    sMenu = "\n"
    sMenu += "Which demographic is residing here?\n"
    sMenu += "0: Rich           [2500sq.m plot and up]\n"
    sMenu += "1: High-income    [1600sq.m plot]\n"
    sMenu += "2: Mid-income     [ 900sq.m plot]\n"
    sMenu += "3: Low-income     [ 600sq.m plot]\n"
    sMenu += "4: Poor           [ 400sq.m plot]\n"

    iLevel_option = misc.get_int(sMenu, 4)
    if iLevel_option == None:
        print("\a")
        return None

    if iLevel_option == 0:
        dNew_housing["demographic"] = "r"
    elif iLevel_option == 1:
        dNew_housing["demographic"] = "h"
    elif iLevel_option == 2:
        dNew_housing["demographic"] = "m"
    elif iLevel_option == 3:
        dNew_housing["demographic"] = "l"
    elif iLevel_option == 4:
        dNew_housing["demographic"] = "p"
    else:
        print("\n\aInvalid choice for port type")
        return

# DESCRIPTION:
    sTxt = ("\nGive a brief description of the area. For example:\n" +
        "'(9x2)x1M [7+1S+1SP]': Seven units in a row, 1 from the side, " +
        "1 panhandle from\nside with two households sharing this building")
    print(sTxt)
    dNew_housing["sDesc"] = input()

    # BUILDING COUNT
    sTxt = ("\nHow many buildings in the group?")
    iNo_of_buildings = misc.get_int(sTxt)
    if iNo_of_buildings == None: return None
    dNew_housing["iNo_of_buildings"] = iNo_of_buildings

    # FLOOR COUNT
    sTxt = ("\nHow many floors does each building have?")
    iFloor_cnt = misc.get_int(sTxt)
    if iFloor_cnt == None: return None
    dNew_housing["iNo_of_floors"] = iFloor_cnt

    # APPARTMENT COUNT
    sTxt = ("\nHow many appartments per floor in this building?")
    iUnits_per_floor = misc.get_int(sTxt)
    if iUnits_per_floor == None: return None
    dNew_housing["iUnits_per_floor"] = iUnits_per_floor

    # TOTAL UNITS
    fTot_units = iNo_of_buildings * iFloor_cnt * iUnits_per_floor
    iTot_units = int(round(fTot_units, 0))
    dNew_housing["iTot_units"] = iTot_units

    # PARKING:
    sMenu = "\n"
    sMenu += "How do you want to calculate car parking available?\n"
    sMenu += "0: Individual houses, with x number of cars per plot\n"
    sMenu += "1: Square footprint, with x and y known in mm.\n"
    sMenu += "2: Footprint, with area in sq.mm is known\n"

    iParking_option = misc.get_int(sMenu, 2)
    if iParking_option == None: return None

    iVeh = None                     # I publish the results of the parking.
    # INDIVIDUAL HOUSES
    if iParking_option == 0:
        sTxt = ("There are {0} plots in this area. Enter number of vehicles " +
            "per plot\nthat can be parked off the street. (Usually 2)")
        sTxt = sTxt.format(iNo_of_buildings)
        iVeh = misc.get_int(sTxt)
        if iVeh == None: return None

        iVeh *= iNo_of_buildings
        dNew_housing["aParking"]["iVeh"] = iVeh

    # SQUARE FOOTPRINT KNOWN SIDES
    elif iParking_option == 1:
        sTxt = ("Enter the first side of the area for parking")
        fParking_x = misc.get_float(sTxt)
        if fParking_x == None: return None

        sTxt = ("Enter the second side of the area for parking, perpendicular" +
            " to the first")
        fParking_y = misc.get_float(sTxt)
        if fParking_y == None: return None

        # Calculate the parking area
        fMap_area = fParking_x * fParking_y
        fMap_scale = dNew_housing["aMap"]["fScale"]
        aParking_area = misc.calc_area(fMap_area, fMap_scale)

        if aParking_area == None: return None

        # We know the real-world scale of the parking.
        # In the real world, a parking bay is 5.5m x 2.5m (13.75sq.m). However,
        # each vehicle needs access to that bay. The above calcuation gives
        # 7.27veh/100sq.m. However, each vehilce needs some space to get to the
        # bay. Hence, I'm using the figure of 6 veh / 100sq.m (600veh/ha)

        # Verify the units of measurement
        if aParking_area["uom"] != "sq.m":
            print("\nUnexpected calculation result for residential parking:\n" +
                "Expected 'sq.m', but got {0}\a".format(aParking_area["uom"]))
            return None
        fSqm_P = aParking_area["qty"]

        sTxt = ("On how many levels are cars parked?")
        iFloors = misc.get_int(sTxt)
        if iFloors == None: return None

        if iFloors > 1 and fSqm_P < 90:
            sTxt = ("\n\aInsufficient space for a ramp " +
                "(1:10 @ h = 3.6m, w = 2.5m). Exiting")
            return None

        if iFloors > 1:
            fSqm_P -= 90    # Take room for the ramp
        fVeh = 6.0 * fSqm_P / 100       # 6 cars per 100 sq.m
        print("fVeh:{0}; fSqm_P:{1}".format(fVeh, fSqm_P))
        iVeh = int(round(fVeh, 0))      # Round off to whole vehicles

        fVeh = iVeh * iFloors           # We need to round off per floor.
        iVeh = int(round(fVeh, 0))      # Round off to whole vehicles

        fVeh = iVeh * iNo_of_buildings  # Parking in each building
        iVeh = int(round(fVeh, 0))      # Round off to whole vehicles

        dNew_housing["aParking"]["iFloors"] = iFloors
        dNew_housing["aParking"]["iVeh"] = iVeh
        dNew_housing["aParking"]["map_a"] = fMap_area

    # BASEMENT PARKING: FOOTPRINT AREA KNOWN
    elif iParking_option == 2:
        sTxt = ("Enter the area of the parking footprint in sq.mm from map.")
        fMap_area = misc.get_float(sTxt)
        if fMap_area == None: return None

        # Calculate the parking area
        fMap_scale = dNew_housing["aMap"]["fScale"]
        aParking_area = misc.calc_area(fMap_area, fMap_scale)
        if aParking_area == None: return None

        # We know the real-world scale of the parking.
        # In the real world, a parking bay is 5.5m x 2.5m (13.75sq.m). However,
        # each vehicle needs access to that bay. The above calcuation gives
        # 7.27veh/100sq.m. However, each vehilce needs some space to get to the
        # bay. Hence, I'm using the figure of 6 veh / 100sq.m (600veh/ha)

        # Verify the units of measurement
        if aParking_area["uom"] != "sq.m":
            print("\nUnexpected calculation result for residential parking:\n" +
                "Expected 'sq.m', but got {0}\a".format(aParking_area["uom"]))
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

        fVeh = iVeh * iNo_of_buildings  # Parking in each building
        iVeh = int(round(fVeh, 0))      # Round off to whole vehicles

        dNew_housing["aParking"]["iFloors"] = iFloors
        dNew_housing["aParking"]["iVeh"] = iVeh
        dNew_housing["aParking"]["map_a"] = fMap_area

    # Save the data in the array
    print("\nThese buildings park {0} vehicles".format(iVeh))

# -- -- -- -- -- -- -- -- -- --
#   UPDATE THE GEO-OBJECT
    dSup_hhold = dGeo_element["aSupply_hholds"]

    # Get the existing data out
    dTot_sup = dSup_hhold["total"]
    aItemised = dSup_hhold["aItemised"]

    # Update total of this particular demographic
    sGroup = dNew_housing["demographic"]            # 'r' to 'p'
    iTot_units = dNew_housing["iTot_units"]         # Household count.
    dTot_sup[sGroup] += iTot_units                  # Add to the grand total

    # Generate the prototype
    dItem = {"sName":None, "r":0, "h":0, "m":0, "l":0, "p":0}

    # Update the item
    dItem["sName"] = dNew_housing["my_id"]          # > 36 blocks possible
    dItem[sGroup] += iTot_units                     # Build the item
    aItemised.append(dItem)                         # Save with suburb

    # UPDATE DATA BASE
    cHousing.insert_one(dNew_housing)               # Housing pushed

    # UPDATE HOST
    xParam = {"geo_code":sGeo_code}
    xNew_data = {"$set":{"aSupply_hholds":dSup_hhold}}
    cDest.update_one(xParam, xNew_data)

    print("\n DATABASE ENTRIES UPDATED ({0})".format(sNew_id))

#-------------------------------------------------------------------------------
# 4: PRETTY-PRINT MANUALLY DATABASE ENTRY TO FILE FOR A SINGLE GEOCODE
#-------------------------------------------------------------------------------
def pretty_print_single(ccTremb):
    """ Writes most of the elements from the database in a human-readable format
    """
    import datetime

    sMenu = "\nPlease Enter the housing identifier (ex: H00-001)"
    print(sMenu)
    sHse_code = input().upper()              # Force to upper case (consistency)

    # Access the database.
    cHouse = db.housing(ccTremb)
    xParam = {"my_id" : sHse_code}
    xRestr = {"_id":0}
    dQuery = cHouse.find(xParam, xRestr)

    # Pull the data and verify the existance
    iNo_of_hits = 0
    dData = ""
    for query in dQuery:
        dData = query
        iNo_of_hits += 1

    if iNo_of_hits != 1:
        sTxt = ("\n\aThere were {0} 'hits' while expecting 1 for [{1}]")
        print(sTxt.format(iNo_of_hits, sHse_code))
        return None

    # Work out a name of the file
    sFile_path = "Logs/h_{0}_pretty.txt".format(sHse_code)
    eSingle_data = open(sFile_path, "w", encoding="utf-8")

# Write the title with timestamp
    sAll = ""                   # Clean state
    xNow = datetime.datetime.now()
    sAll += "Pretty print Housing request was generated on {0}\n".format(xNow)

# Identifiation information
    sAll += "----------\n"
    sAll += "my_id: {0}\n".format(dData["my_id"])

# Name of the block / Area
    sName_lat = dData["aName"]["lat"]
    sName_cyr = dData["aName"]["cyr"]
    sAll += "Name: '{0}' / '{1}'\n".format(sName_lat, sName_cyr)

# Host identification
    sGeo_code = dData["host_geo_code"]
    cDest = db.destinations(ccTremb)   # Database of host
    aName = misc.verify_geo_code(sGeo_code, cDest)
    sAll += "----------\n"
    sLat = aName["lat"]
    sCyr = aName["cyr"]
    sTxt = "Host: [{0}] '{1}' / '{2}'\n"
    sTxt = sTxt.format(sGeo_code, sLat, sCyr)
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

    else:
        sAll +=  ">   No map declared\n"

# More about the buildings
    sAll += "----------\n"
    sAll += "Building(s):\n"
    sAll += ">   Description: {0}\n".format(dData["sDesc"])
    sAll += ">   Type: {0}\n".format(dData["type"])
    sAll += ">   Sub-type: {0}\n".format(dData["sub_type"])
    sAll += ">   Demographic code: '{0}'\n".format(dData["demographic"])
    sAll += ">   Units per floor:  {0}\n".format(dData["iUnits_per_floor"])
    sAll += ">   Number of floors: {0}\n".format(dData["iNo_of_floors"])
    sAll += ">   Number of buildings: {0}\n".format(dData["iNo_of_buildings"])
    sAll += ">   Total units: {0}\n".format(dData["iTot_units"])

    # Building footprint, if data is available
    fQty = dData["aFpt_bldg"]["qty"]
    sUom = dData["aFpt_bldg"]["uom"]
    sTxt = ">   Building footprint: "
    if fQty == None:
        sTxt += "N/A\n"
    else:
        sTxt += "{0:,}{1}\n".format(fQty, sUom)
    sAll += sTxt

    # Property footprint, if data is available
    fQty = dData["aArea_plot"]["val"]
    sUom = dData["aArea_plot"]["uom"]
    sTxt = ">   Area of plot: "
    if fQty == None:
        sTxt += "N/A\n"
    else:
        sTxt += "{0:,}{1}\n".format(fQty, sUom)
    sAll += sTxt

# More about the parking situation
    aParking = dData["aParking"]
    sAll += "----------\n"
    sAll += "Parking (cars):\n"
    sAll += ">   Levels: {0}\n".format(aParking["iFloors"])
    sAll += ">   Total vehicle spaces: {0}\n".format(aParking["iVeh"])
    sAll += ">   Area on map: {0}sq.mm\n".format(aParking["map_a"])

# Write to the file
    print("Please see: {0}".format(sFile_path))
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()


#-------------------------------------------------------------------------------
# SUB-MENU
#-------------------------------------------------------------------------------
def sub_menu():
    """ Provides choices for the land mapped in CAD """

    ccTremb = db.connect()
    cStation = db.stations(ccTremb)
    sSub_menu = """

HOUSING SUB-MENU (H):
.:  Exit
1:  Add a housing
4:  Pretty print

""" # Closes the multi=line txt

    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

    # User has made their choice. Now, process it.
        if sInput == ".":           # Exit
            bExit = True
        elif sInput == "1":         # New
            add_housing(ccTremb)
#        elif sInput == "2":          # All the stations
#            view_all(ccTremb)
#        elif sInput == "3":         # View single
#            view_single(ccTremb)
        elif sInput == "4":         # Formats the little bit of data
            pretty_print_single(ccTremb)
        else:
            bExit = True
