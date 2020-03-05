""" Community services keeps track of how which 'items' (clinics, hospitals,
police stations, ect) have been drawn on the map. It is intended to be used on
a 50k (and lower) maps, where each plot of housing is defined. A database is
opened which keeps track of all the items declared. This will allow for easier
modification in the future. The data provided is intended to be unbalanced. The
 demand and supply balancing system will be provided later in time.
"""

import modules.x_database as db
import modules.x_misc as misc
import modules.d_destinations as d_py

#-------------------------------------------------------------------------------
# 1. Add Community items
#-------------------------------------------------------------------------------
def add_community_services(ccTremb):
    """ Adds the the following items to the database. It takes data from the
    map. The actual number of employees will be determined later. These can be
    placed first; its service region can be edited later. Another method will
    update these and their hosts. The list of items accessed through here is:
            5YP: Community Police station,
            5YF: Community Fire station,
            5YH: Community clinics,
            5YG: Community governance,
            ED0: Pre-school,
            ED1: Primary School,
            ED2: Middle School,
            ED3: High School,
            OAH: Standard Old Age Home,
            5SŠ: Community shop ("Small Šop"),
            5LX: Community Libraries,
            5TH: Community Theatres,
            5PO: Community Post Offices.
    """

    # Obtain the highest "my_id" code that is registered in the database.
    xParam = {}
    xRestr = {"_id":0, "my_id":1}
    cCommunity = db.community_services(ccTremb)
    dId_query = cCommunity.find(xParam, xRestr)
    iHighest, aEvery_id = misc.find_highest_id(dId_query)

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
    sNew_id = "A{0}-{1}".format(sBase36_5[:2], sBase36_5[2:])
    print("\nNext id is {0}".format(sNew_id))

# START GETTING THE USER TO ENTER THE NEW DATA.
    # Open a blank dictionary, so that the elements are arranged in a certain
    # order.
    dNew_service = {
        "my_id":sNew_id,
        "host_geo_code":None,
        "aName":{"lat":None, "cyr":None},  # Is the block of flats named?
        "type_code":None,       # "5YP" for example
        "type_name":"",         # "Police"
        "iNo_of_units":1,       # Multiple units operating from one site.
        "sub_type":None,        # RFU
        "aServes":[],           # Geo-codes of commuinties it serves.
        "iClients":0,           # Quick summary of clients supplied
        "iCapacity":0,          # Summary of how much we can hold
        "sNotes":"",            # Irregular building
        "aMap":{
            "sRegion":None,
            "iYear":None,
            "fScale":None,
            "x":None,
            "y":None,
            "a":None
        },
        "aFtp_bldg":{"qty":None, "uom":None},
        "aArea_plot":{"qty":None, "uom":None},
    }

# HOST
    cDest = db.destinations(ccTremb)                    # To verify the geocode
    sTxt = ("\nWho is hosting this community service?"+
            " Please enter thier geo-code.")
    print(sTxt)
    sGeo_code = input().upper()

    dHost_element = misc.get_geo_element(sGeo_code, cDest)
    if dHost_element == None: return

    dNew_service["host_geo_code"] = sGeo_code
    aHost_name = dHost_element["aName"]
    sTxt = "\nHosted by {0} / {1}".format(aHost_name["lat"], aHost_name["cyr"])
    print(sTxt)

# MAKE A LIST OF THE SERVICES
    cCity_services = db.city_services_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dCity_query = cCity_services.find(xParam, xRestr)

    # Copy out the query
    dCity_copy = []
    for dItem in dCity_query:
        dCity_copy.append(dItem)

    # Setup the menu
    sMenu = ("\nWhich service are you adding? (Invalid entry will exit)\n")
    iCnt = 0
    for dOne_service in dCity_copy:
        iCnt += 1
        sCode = dOne_service["code"]
        sName = dOne_service["name"]
        sMenu += ("{0}: [{1}] {2}\n".format(iCnt, sCode, sName))

    # Print the menu and get the response
    iChoice = misc.get_int(sMenu, 13)
    if iChoice == None: return None

    # Select the service
    dSvc = dCity_copy[iChoice-1]    # Count started at one!

    # Record the code
    dNew_service["type_code"] = dSvc["code"]    # 5YP for example
    dNew_service["type_name"] = dSvc["name"]    # Police for example

# MAP REFERENCE
    sMap = dSvc["name"]
    dData = misc.get_map_input(ccTremb, sMap)  # Asks for user to input stuff.
    if dData in [None, True]:                  # No map selected
        print("\n\aInvalid entry from the map. Exiting")
        return None

    # Transfer data through.
    dNew_service["aMap"] = dData["dMap"]
    dNew_service["aArea_plot"] = dData["dArea"]

# BUILDING:
    sTxt = "Is the size of the actual building(s) known?"
    sYn_bldg = misc.get_binary(sTxt)
    if sYn_bldg == None: return None

    if sYn_bldg == "Y":
        sTxt = "\nEnter the footprint of the building in sq.mm from map."
        fBldg_ftp = misc.get_float(sTxt)
        if fBldg_ftp == None: return None

        # Calculate area
        fScale = dNew_service["aMap"]["fScale"]
        dNew_service["aFpt_bldg"] = misc.calc_area(fBldg_ftp, fScale)

# NAME THE FACILITY
    aName = misc.building_name()
    if aName == None: return None
    if aName != False:      # A name was chosen
        dNew_service["aName"] = aName

# Building count
    sTxt = ("How many units operate from this facility?")
    iNo_of_units = misc.get_int(sTxt)
    if iNo_of_units == None: return None
    dNew_service["iNo_of_units"] = iNo_of_units

# Calculate total customer capacity:
    fTot_cust = iNo_of_units * dSvc["capacity"]
    iTot_cust = int(round(fTot_cust, 0))        # Just to be sure.
    dNew_service["iCapacity"] = iTot_cust

# SERVICES: WHICH AREA DOES THIS FACILITY SERVICE
# While here, show live updates of the service demand.
    sDgfx_code = dSvc["serves"]             # iTOT-PAX for example

    bDone = False                                       # Multiple areas.
    while bDone == False:
        sTxt = ("\nThis facility serves the people of ___." +
                "\n(Enter the geo-code of the entity OR Press '.' to exit loop")
        print(sTxt)
        sGeo_code = input().upper()
        if sGeo_code in ["", None, "."]:
            bDone = True
            continue

        # Verify the geo-code
        dCust_element = misc.get_geo_element(sGeo_code, cDest)
        if dCust_element == None:
            bDone = True
            continue

        # Geocode verified, add the geo code to the list
        dNew_service["aServes"].append(sGeo_code)

        sLat_name = dCust_element["aName"]["lat"]
        sCyr_name = dCust_element["aName"]["cyr"]

        # Sort out the capacity as we go along.
        sTxt = "{0} / {1}:\n".format(sLat_name, sCyr_name)
        sTxt += "{0} is ".format(sDgfx_code)

        aDgfx = dCust_element["aDemographics"]          # Shorter access
        if aDgfx == {}:
            dNew_service["sNotes"] += " {0}*,".format(sGeo_code)
            sTxt += ("N/A")
        else:
            iClients = aDgfx[sDgfx_code]
            sTxt += ("{0}\n".format(iClients))
            dNew_service["iClients"] += iClients
            iNs_clt = dNew_service["iClients"]
            iNs_cap = dNew_service["iCapacity"]
            fPercentage = iNs_clt / iNs_cap
            sPercentage = "{:.3f}".format(fPercentage)      # Hopefully "0.344"
            sTxt_a = ("Total clients: {0} / {2} = ({1} of capacity)")
            sTxt += sTxt_a.format(iNs_clt, sPercentage, iNs_cap)
        print(sTxt)

    # end of while loop, servicing the facilities.
    print("Enter comments (if any)")
    dNew_service["sNotes"] += "| "
    dNew_service["sNotes"] += input()

# UPDATE THE WORKPLACE SUPPLY.
    # Create the element first. It will either be overridden or a new entry will
    # be created
    fDenominator = dNew_service["iCapacity"] * iNo_of_units
    if fDenominator == 0.00:
        print("\n\aDivide by zero error caught during capacity calc. Exiting")
        return None
    fNumerator = dNew_service["iClients"]
    fCapacity = fNumerator / fDenominator
    sCapacity = "{:.3}".format(fCapacity)

    dThe_item = {
        "iCnt": iNo_of_units,            # How many pre-schools in this facility
        "sCode": dSvc["code"],           # 5YH for example
        "sName": dNew_service["my_id"],  # A00-001 for example (unique)
        "lServices": dNew_service["aServes"], # Geo-codes within the scope
        "fCapacity": sCapacity,              # Needs to be calculated
    }

    print(dThe_item)            # for aDemand_workforce
    print(dNew_service)         # Own database entry

# WRITE TO DATABASE
    aSupply_workplace = dGeo_element["aSupply_workplace"]
    aSupply_workplace.append(dThe_item)

    xParam = {"geo_code":dNew_service["host_geo_code"]}
    xNew_data = {"$set": {
        "aSupply_workplace": aSupply_workplace,
    }}
    cDest.update_one(xParam, xNew_data)
    cCommunity.insert_one(dNew_service)

    print(">>> Databases updated ({0})".format(dNew_service["my_id"]))

#-------------------------------------------------------------------------------
# 2: VIEW THE CHILDREN'S DEMAND
#-------------------------------------------------------------------------------
def view_child_demands(ccTremb):
    """ Draws up a table showing the children and their demand for police
    stations, clinics, ect """

    # Get the parent's geo-code
    sMenu = "\nEnter the geo-code of the parent (ex. VAA-00)"
    print(sMenu)
    sParent = input().upper()

    # Get the parent
    cDest = db.destinations(ccTremb)                    # Get the database
    dParent = misc.get_geo_element(sParent, cDest)
    if dParent == None: return None

    # Open a text file where a copy of the information will be written to.
    if sParent == "*":
        sFile_name = "world"                    # Exception in naming convention
    else:
        sFile_name = sParent

    # Work out a name of the file
    sFile_path = "Logs/a_{0}_child_demands.txt".format(sFile_name)
    eChild_data = open(sFile_path, "w", encoding="utf-8")

    sHeading = "Children and their service demands\n"
    eChild_data.write(sHeading)

    # Get the unit capacities:
    cCity_services = db.city_services_const(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dCity_query = cCity_services.find(xParam, xRestr)

    # Copy out the query
    aCity_copy = []
    for dItem in dCity_query:
        aCity_copy.append(dItem)

    sSubtitle = "{:>32.32} :".format("Service code")
    sBreak    = "{:>32.32} :".format("-"*32)
    for dService in aCity_copy:
        sSubtitle += " {:^6.6}:".format(dService["code"])
        sBreak += "-"*7 + ":"           # Creates a visual break
    eChild_data.write(sSubtitle + "\n")
    eChild_data.write(sBreak + "\n")

# LOOP THROUGH EACH CHILD
    for child in dParent["aChildren"]:
        # Query each child on their identifier
        xParam = {"my_id": child}
        xRestr = {"_id":0}
        dChild_query = cDest.find(xParam, xRestr)

        # Go through every child' details
        for dThe_child in dChild_query:      # The query is an array.
        # Get the names out
            sChd_id = dThe_child["geo_code"]
            sChd_lat = dThe_child["aName"]["lat"]
            sChd_cyr = dThe_child["aName"]["cyr"]
            sLine = "{0:>7.7}: {1:>10.10} / {2:<10.10} :"   # <Justfy>Length.precision
            sLine = sLine.format(sChd_id, sChd_lat, sChd_cyr)

        # Start looping through the services
            aDgfx = dThe_child["aDemographics"]

            # Go through each of the services:
            for dService in aCity_copy:
                if aDgfx == {}: # No data for demographics
                    sLine += " {0:^6.6}:".format("N/A")
                    continue    # Alternative to 'else'
                sServes = dService["serves"]        # Population group concerned
                iCapacity = dService["capacity"]    # Customers per unit
                fUnits_reqd = aDgfx[sServes] / iCapacity # Calculate!
                sLine += " {0:6.2f}:".format(fUnits_reqd)   # "|123.45"

            sLine += "\n"
            eChild_data.write(sLine)

        # End of going through each child in the query
    # End of going through each child in the parent
    eChild_data.write(sBreak + "\n")
    eChild_data.write(sSubtitle + "\n")
    eChild_data.close()

#-------------------------------------------------------------------------------
# SUB-MENU
#-------------------------------------------------------------------------------
def sub_menu():
    """ Provides choices for the land mapped in CAD """

    ccTremb = db.connect()
    cStation = db.stations(ccTremb)
    sSub_menu = """

COMMUNITY SERVICES SUB-MENU (A):
.:  Exit
1:  Add a community service
2:  View children's demands (tabular)

""" # Closes the multi=line txt

    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

    # User has made their choice. Now, process it.
        if sInput == ".":           # Exit
            bExit = True
        elif sInput == "1":         # New
            add_community_services(ccTremb)
        elif sInput == "2":          # All the stations
            view_child_demands(ccTremb)
#        elif sInput == "3":         # View single
#            view_single(ccTremb)
#        elif sInput == "4":         # Formats the little bit of data
#            pretty_print_single(ccTremb)
        else:
            bExit = True
