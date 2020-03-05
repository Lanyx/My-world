""" Stations and Ports deals with the basics of 'organised transport'. It
provides information on Train stations, Bus depos, Ports, Airports. """

import modules.x_database as db
import modules.x_misc as misc
import modules.d_destinations as d_py

#-------------------------------------------------------------------------------
# 1. Add station or port
#-------------------------------------------------------------------------------
def add_station(ccTremb):
    """ Adds details of a station to the database """

    # Obtain the highest "my_id" code that is registered in the database.

    # Get a list of all the registered base-36 codes
    xParam = {}
    xRestr = {"_id":0, "my_id":1}
    cStation = db.stations(ccTremb)
    dId_query = cStation.find(xParam, xRestr)
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
    sNew_id = "S{0}-{1}".format(sBase36_5[:2], sBase36_5[2:])

# START GETTING THE USER TO ENTER THE NEW DATA.
    # Open a blank dictionary, so that the elements are arranged in a certain
    # order.
    dNew_port = {
        "my_id":sNew_id,
        "host_geo_code":None,
        "aName":{"lat":None, "cyr":None},
        "type":None,
        "sub_type":None,
        "level":None,
        "aMap":{
            "sRegion":None,
            "iYear":None,
            "fScale":None,
            "x":None,
            "y":None,
            "a":None
        },
        "aArea":{"qty":None, "uom":None},
        "lServices":[],
        "lWarehouse":[],
        "iLoading_zones":0,
    }

# HOST
    cDest = db.destinations(ccTremb)                    # To verify the geocode
    sTxt = ("\nWho is hosting this station/port? Please enter thier geo-code.")
    print(sTxt)
    sGeo_code = input().upper()

    aHost_name = misc.verify_geo_code(sGeo_code, cDest)
    if aHost_name == None: return

    dNew_port["host_geo_code"] = sGeo_code
    sTxt = "\nHosted by {0} / {1}".format(aHost_name["lat"], aHost_name["cyr"])
    print(sTxt)

# TYPE
    sMenu = "\n"
    sMenu += "What type of a station or port is it?\n"
    sMenu += "0: Rail\n"
    sMenu += "1: Road\n"
    sMenu += "2: Water\n"
    sMenu += "3: Air\n"

    iType_option = misc.get_int(sMenu, 3)
    if iType_option == None:
        print("\a")
        return None

    if iType_option == 0:
        dNew_port["type"] = "Rail"
    elif iType_option == 1:
        dNew_port["type"] = "Road"
    elif iType_option == 2:
        dNew_port["type"] = "Water"
    elif iType_option == 3:
        dNew_port["type"] = "Air"
    else:
        print("\n\aInvalid choice for port type")
        return

# SUB-TYPE
    sMenu = "\n"
    sMenu += "What is transported?\n"
    sMenu += "0: Passangers    (PAX)\n"
    sMenu += "1: Freight       (F)\n"
    sMenu += "2: Livestock     (L/S)\n"

    iType_option = misc.get_int(sMenu, 2)
    if iType_option == None:
        print("\a")
        return None

    if iType_option == 0:
        dNew_port["sub_type"] = "Pax"
    elif iType_option == 1:
        dNew_port["sub_type"] = "Freight"
    elif iType_option == 2:
        dNew_port["sub_type"] = "Livestock"
    else:
        print("\n\aInvalid choice for port type")
        return

# LEVEL
    sMenu = "\n"
    sMenu += "What level is the station or port on?\n"
    sMenu += "0: International                   ['0V9'->'0Q1']\n"
    sMenu += "1: National / Inter-Provincial     ['V'->'L']\n"
    sMenu += "2: Provincial / Inter-District     ['GY'->'VA']\n"
    sMenu += "3: District / Inter-County         ['GYN'->'GY0']\n"
    sMenu += "4: County / Inter-Municipal        ['GYN-2'->GYN-0] \n"
    sMenu += "5: Municipal / Intra-Municipal     ['VAA-0A'->'VAA-0B'])\n"

    iLevel_option = misc.get_int(sMenu, 5)
    if iLevel_option == None:
        print("\a")
        return None

    if iLevel_option == 0:
        dNew_port["level"] = "Int'l"
    elif iLevel_option == 1:
        dNew_port["level"] = "Nat'l"
    elif iLevel_option == 2:
        dNew_port["level"] = "Prov."
    elif iLevel_option == 3:
        dNew_port["level"] = "Dist."
    elif iLevel_option == 4:
        dNew_port["level"] = "Cnty."
    elif iLevel_option == 5:
        dNew_port["level"] = "Muni."
    else:
        print("\n\aInvalid choice for port type")
        return

# MAP REFERENCE
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
    print("\nOn which map is this station/port?")

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
        print("\nInput is not a numeric value. Returning to menu")
        return None

    # Get the details from the dictionary and write them into the destinations
    # entry.
    iInput = int(sInput)
    if(iInput == 0):
        dNew_port["aMap"]["sRegion"] = "No Map"
        dNew_port["aMap"]["iYear"] = None
        dNew_port["aMap"]["fScale"] = None
    elif(iInput > iCnt):
        print("\nChoice out of range. Returning to menu")
        return None
    else:
        iIdx = iInput - 1
        dNew_port["aMap"]["sRegion"] = dMap_copy[iIdx]["sRegion"]
        dNew_port["aMap"]["iYear"] = dMap_copy[iIdx]["iYear"]
        dNew_port["aMap"]["fScale"] = dMap_copy[iIdx]["fScale"]

# Map location: Co-ordinates on the speciied CAD map.
    if(dNew_port["aMap"]["fScale"] != None):
        # This only works if the map exists.
        sQuestion = "\nEnter the x-coordinate from the map:"
        fX = misc.get_float(sQuestion, None, True)
        if fX == None: return None
        dNew_port["aMap"]["x"] = fX

        sQuestion = "\nEnter the y-coordinate from the map:"
        fY = misc.get_float(sQuestion, None, True)
        if fY == None: return None
        dNew_port["aMap"]["y"] = fY

        sQuestion = "\nEnter the area in mm2 from the map:"
        fA = misc.get_float(sQuestion)
        if fA == None: return None
        dNew_port["aMap"]["a"] = fA

    # Calcluate the area.
        dArea = misc.calc_area(
                dNew_port["aMap"]["a"],
                dNew_port["aMap"]["fScale"]
        )
        if dArea == None: return None
        # Compensate for inconsistency
        dArea_2 = {"val": dArea["qty"], "uom": dArea["uom"]}
        dNew_port["aArea"] = dArea_2
    # End of map location entry

# NAME IT!
    bExit = False
    while bExit == False:
        sMenu = "\nDo you want a to use host's name/a random name?"
        sRand_name_yn = misc.get_binary(sMenu)
        if sRand_name_yn == None: return None

        sName_only_lat = ""
        sName_only_cyr = ""

    # Manual entry:
        if sRand_name_yn == "N":
            print ("\nPlease enter the name of the station / port in" +
                   "(Use international Keyboard)")
            sName_only_lat = input()

            # User entered name in Cyrillic
            print ("\nНапиш име стацйи люб порту в Цырполюю. "
                  +"(пшэлаьч клавятурэ рэьчне)")
            sName_only_cyr = input()

    # Randomly generated Name
        elif sRand_name_yn == "Y":
            # Operated by an external routine
            import modules.x_random_names as rnd_name

            # We are storing the random names from the various systems here.
            # Hence, we will build up one set of arrays for the user to
            #choose
            aLat = []
            aCyr = []

        # Host name
            aLat.append(aHost_name["lat"])
            aCyr.append(aHost_name["cyr"])

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

        # Export the final names
            sName_only_lat = aLat[iChoice]
            sName_only_cyr = aCyr[iChoice]
        # Prepare post-fix
        sLat_Intl = ""
        sCyr_Intl = ""
        if dNew_port["level"] == "Int'l":
            sLat_Intl = "International"
            # The joys of Slavic grammar!
            if dNew_port["type"] in ["Rail"]:
                sCyr_Intl = "Меьдзыщнародова"
            elif dNew_port["type"] in ["Water", "Road"]:
                sCyr_Intl = "Меьдзыщнародовы"
            elif dNew_port["type"] in ["Air"]:
                sCyr_Intl = "Меьдзыщнародовэ"

        # Type of transport
        sLat_B = ""
        sCyr_B = ""

        # Rail ####################################################
        if dNew_port["type"] == "Rail":
            if dNew_port["sub_type"] == "Pax":
                sLat_B = "Train Station"
                sCyr_B = "Стаця Колеёва"

            elif dNew_port["sub_type"] == "Freight":
                sLat_B = "Freight Station"
                sCyr_B = "Стаця Товарова"

            elif dNew_port["sub_type"] == "Livestock":
                sLat_B = "Livestock Station"
                sCyr_B = "Стаця Звъежаьт"

        # Road - - - - - - - - - - - - - - - - - - - - - - - - - - -
        elif dNew_port["type"] == "Road":
            if dNew_port["sub_type"] == "Pax":
                sLat_B = "Bus Station"
                sCyr_B = "Двожэс Алтобусовы"

            elif dNew_port["sub_type"] == "Freight":
                sLat_B = "Truck Depot"
                sCyr_B = "Двожэс Товаровы"

            elif dNew_port["sub_type"] == "Livestock":
                sLat_B = "Livestock Depo"
                sCyr_B = "Двожэс Звъежэьтьи"

        # Water ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        elif dNew_port["type"] == "Water":
            if dNew_port["sub_type"] == "Pax":
                sLat_B = "Passanger Harbour"
                sCyr_B = "Порт Особовы"

            elif dNew_port["sub_type"] == "Freight":
                sLat_B = "Freight Harbour"
                sCyr_B = "Порт Товаровы"

            elif dNew_port["sub_type"] == "Livestock":
                sLat_B = "Livestock Harbour"
                sCyr_B = "Порт Звъежэьтьи"

        # Air > > > -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - < < <
        elif dNew_port["type"] == "Air":
            if dNew_port["sub_type"] == "Pax":
                sLat_B = "Airport"
                sCyr_B = "Лётниско"

            elif dNew_port["sub_type"] == "Freight":
                sLat_B = "Freight Airport"
                sCyr_B = "Лётниско Товаровэ"

            elif dNew_port["sub_type"] == "Livestock":
                sLat_B = "Livestock Airport"
                sCyr_B = "Лётниско Звъежэьцэ"
        else:
            print("Invalid choice. Exiting")
            return None

        # Full Latin name
        if sLat_Intl == "":
            sTxt = "{0} {1}".format(sName_only_lat, sLat_B)
        else:
            sTxt = "{0} {1} {2}".format(sName_only_lat, sLat_Intl, sLat_B)
        dNew_port["aName"]["lat"] = sTxt

        # Cyrillc grammar
        if sCyr_Intl == "":
            sTxt = "{1} о им. {0}".format(sName_only_cyr, sCyr_B)
        else:
            sTxt = "{1} {2} о им. {0}"
            sTxt = sTxt.format(sName_only_cyr, sCyr_Intl, sCyr_B)
        dNew_port["aName"]["cyr"] = sTxt


    # Confirm the name choice
        sNew_lat = dNew_port["aName"]["lat"]
        sNew_cyr = dNew_port["aName"]["cyr"]
        sMenu = "Are the names:\n'{0}'\n'{1}' OK?"
        sMenu = sMenu.format(sNew_lat, sNew_cyr)
        sNames_ok_yn = misc.get_binary(sMenu)
        if sNames_ok_yn == "Y": bExit = True
    # End of 'its named'


# SERVICES: WHICH AREA DOES THIS FACILITY SERVICE
    bDone = False                                       # Multiple areas.
    while bDone == False:
        sTxt = ("\nThis station/port serves the people of ___." +
                "\n(Enter the geo-code of the entity OR Press '.' to exit loop")
        print(sTxt)
        sGeo_code = input().upper()
        if sGeo_code in ["", None, "."]:
            bDone = True
            continue

        # Verify the geo-code
        aName = misc.verify_geo_code(sGeo_code, cDest)
        if aName == None:
            bDone = True
            continue

        # Geocode verified, add the geo code to the list
        dNew_port["lServices"].append(sGeo_code)

        sLat_name = aName["lat"]
        sCyr_name = aName["cyr"]
        print("({0} / {1})".format(sLat_name, sCyr_name))
    # end of while loop

# WAREHOUSE:
    lSta_Whs = dNew_port["lWarehouse"]  # Station warehouse
    for sTown in dNew_port["lServices"]:
    # Passanger or freight?
        if dNew_port["sub_type"] == "Pax":
            aData = {}
            # Travel demand: Why not model on Newton's equation of gravitation:
            # F = G*m1*m2 / r^2. Where, 'm' would be the population.
            xParam = {"geo_code":sTown}
            xRestr = {"_id":0, "aDemographics":1}
            dRun_query = cDest.find(xParam, xRestr)
            for query in dRun_query:
                aData = query["aDemographics"]

    # Freight or livestock:
        else:
        # Pull the data from the warehouses.
            dClt_whs = []       # List, client warehouse
            xParam = {"geo_code":sTown}
            xRestr = {"_id":0, "aWarehouse":1}
            dRun_query = cDest.find(xParam, xRestr)
            for query in dRun_query:
                dClt_whs = query["aWarehouse"]
            # The could be no data in the warehouse
            if dClt_whs == {}:
                continue

        # Extract the data from the warehouse
            for sShelf in dClt_whs:
            # Pull the data apart: look what is on the 'shelf'
                dContent = dClt_whs[sShelf]
                sResource = dContent["resource"].lower()
                fAmount = dContent["annual_output"]
                xUnits = dContent["units"]

                if xUnits == "t/yr":
                    xUnits = "t/wk"
                elif xUnits == "kg/yr":
                    xUnits = "kg/wk"
                elif xUnits == "kt/yr":
                    xUnits = "kt/wk"
                else:
                    print("Units are not presented as weight per year")

                # We have "shelves" in the warehouse already
                bNot_found = True
                for dSta_whs_shelf in lSta_Whs:
                # Find the correct shelf to add the contents.
                    if dSta_whs_shelf["resource"] != sResource:
                        continue
                    if dSta_whs_shelf["units"] != xUnits:
                        print("\n\aUnits mismatch at the warehouse. EXITING")
                        return None

                    fWeekly_produce = round(fAmount / 52, 2)
                    fWeekly_total = dSta_whs_shelf["weekly_output"]
                    fSub_tot = round(fWeekly_total + fWeekly_produce, 2)
                    dSta_whs_shelf["weekly_output"] = fSub_tot
                    bNot_found = False

                # We need to add another shelf to the warehouse:
                if bNot_found == True:
                    dEntry = {}
                    dEntry["resource"] = sResource
                    # NOTE: Logistics run on weekly cycles.
                    dEntry["weekly_output"] = round(fAmount / 52, 2)
                    dEntry["units"] = xUnits
                    lSta_Whs.append(dEntry)
                # End of warehouse shelf created
            # end of going through each of the client's shelves
        # end of freight/livestock vs passangers
    # end of going through the towns on the include list.

    fTot_weight = 0.0
    for dEntry in dNew_port["lWarehouse"]:
        sName = dEntry["resource"]
        fAmount = dEntry["weekly_output"]
        sUnits = dEntry["units"]
        if sUnits == "t/wk":
            fTot_weight += fAmount              # Publish total weight
        elif sUnits == "kt/wk":
            fTot_weight += fAmount * 1000
        elif sUnits == "kg/wk":
            fTot_weight += fAmount / 1000
        sTxt = "{0}: {1}{2}".format(sName, fAmount, sUnits)
        print(sTxt)

    if len(dNew_port["lWarehouse"]) > 0:
        fTot_weight = round(fTot_weight, 3)         # Round off .
        fTot_daily = fTot_weight / 5.0              # MON to FRI
        fTot_daily = round(fTot_daily, 3)
        sTxt = "-------------\n"
        sTxt += "TOTAL: {0}t/wk\n".format(fTot_weight)
        sTxt += "TOTAL: {0}t/day\n".format(fTot_daily)
        print(sTxt)


# Number of loading bays
    sTxt = ("\nEnter the number of 'loading zones'. " +
        "Take into account the imports")
    iLoading_zones = misc.get_int(sTxt)
    if iLoading_zones == None: return

    dNew_port["iLoading_zones"] = iLoading_zones

# ATTACH TO HOST
    if dNew_port["type"] == "Rail":
        if dNew_port["sub_type"] == "Pax":
            sInd_code = "QP1" # Passanger operations
        else:
            # Freight / livestock operations
            sInd_code = "QF1"

    # ROAD TRANSPORT
    elif dNew_port["type"] == "Road":
        if dNew_port["sub_type"] == "Pax":
            sInd_code = "QB1"   # Bus operations
        else:
            sInd_code = "QT1"   # Truck port. Currently at 20t / trip

    # Air TRANSPORT
    elif dNew_port["type"] == "Air":
        if dNew_port["sub_type"] == "Pax":
            sInd_code = "QA1"   # Passanger air ops
        else:
            sInd_code = "QG1"   # Freight air ops


    dBriefcase = {
        "ccTremb": ccTremb,              # Link to all the databases
        "sGeo_code": dNew_port["host_geo_code"],  # of the host
        "sInd_code": sInd_code,          # Passanger or Freight?
        "sName_lat": dNew_port["aName"]["lat"],  # Don't overkill it.
        "sYour_id": dNew_port["my_id"],  # When constructed in city, link it!
        "aArea": dNew_port["aArea"],     # Footprint
        "iNo_of_builds":1,               # Number of stations.
        "lServices": dNew_port["lServices"], # Who makes use of this?
        "fCapacity": None,               # How much is used (schools, ect)
    }

    xFeedback = d_py.add_wkp_auto(dBriefcase)
    if xFeedback == None: return

    cStation.insert_one(dNew_port)
    print("\n>>>\nNew station added")

#-------------------------------------------------------------------------------
# 2: ALL STATIONS PRETTY PRINTED TO FILE
#-------------------------------------------------------------------------------
def view_all(ccTremb):
    """ Writes all the entries to a single file
    """
    import datetime

    # Access the database.
    cStation = db.stations(ccTremb)
    xParam = {}
    xRestr = {"_id":0}
    dQuery = cStation.find(xParam, xRestr)

    # Work out a name of the file
    sFile_path = "Logs/s_all.txt"
    eSingle_data = open(sFile_path, "w", encoding="utf-8")

    # Add the timestamp
    sAll = "All the stations at once"
    xNow = datetime.datetime.now()
    sAll += "Pretty print information was generated on {0}\n".format(xNow)

    # Pull the data and verify the existance
    for dData in dQuery:
    # S00-001 (St. Margret) [GYN-2]:
        sTxt = "\n{0} ({1}) [{2}]:\n"
        sAll += sTxt.format(
            dData["my_id"],
            dData["aName"]["lat"],
            dData["host_geo_code"]
        )
#        sAll += "\n{0} @ {1}:\n".format(dData["my_id"], dData["host_geo_code"])
    # St Margret Freight Station / Стаця Товарова о им. Сьв Гося
        sAll += ">   ({0} / {1})\n".format(
                        dData["aName"]["lat"], dData["aName"]["cyr"])
    # Cnty. Rail-Freight
        sAll += ">   {0} {1}-{2}\n".format(
                        dData["level"], dData["type"], dData["sub_type"])
    # GYN-2, GYN-8
        sTxt = ""
        for dResource in dData["lWarehouse"]:
            sTxt += " {0},".format(dResource["resource"])
        if sTxt != "":
            sAll += ">  {0}\n".format(sTxt)

# Write to the file
    print("Please see: {0}".format(sFile_path))
    eSingle_data.write("{0}\n".format(sAll))
    eSingle_data.close()


#-------------------------------------------------------------------------------
# 3: EXPORT DATABASE ENTRY TO FILE FOR A SINGLE STATION CODE
#-------------------------------------------------------------------------------
def view_single(ccTremb):
    """ Writes all the elements of the database to a text file"""
    sMenu = "\nPlease Enter the station identifier (ex: S00-001)"
    print(sMenu)
    sSta_code = input().upper()              # Force to upper case (consistency)

    # Access the database.
    cStation = db.stations(ccTremb)
    xParam = {"my_id" : sSta_code}
    xRestr = {"_id":0}
    dQuery = cStation.find(xParam, xRestr)

    # Pull the data and verify the existance
    iNo_of_hits = 0
    dData = ""
    for query in dQuery:
        dData = query
        iNo_of_hits += 1

    if iNo_of_hits != 1:
        sTxt = ("\n\aThere were {0} 'hits' while expecting 1 for [{1}]")
        print(sTxt.format(iNo_of_hits, sSta_code))
        return None

    # Work out a name of the file
    sFile_path = "Logs/s_{0}_single.txt".format(sSta_code)
    eSingle_data = open(sFile_path, "w", encoding="utf-8")
    sHeading = ("Database extract\n")

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

    sMenu = "\nPlease Enter the station identifier (ex: S00-001)"
    print(sMenu)
    sSta_code = input().upper()              # Force to upper case (consistency)

    # Access the database.
    cStation = db.stations(ccTremb)
    xParam = {"my_id" : sSta_code}
    xRestr = {"_id":0}
    dQuery = cStation.find(xParam, xRestr)

    # Pull the data and verify the existance
    iNo_of_hits = 0
    dData = ""
    for query in dQuery:
        dData = query
        iNo_of_hits += 1

    if iNo_of_hits != 1:
        sTxt = ("\n\aThere were {0} 'hits' while expecting 1 for [{1}]")
        print(sTxt.format(iNo_of_hits, sSta_code))
        return None

    # Work out a name of the file
    sFile_path = "Logs/s_{0}_pretty.txt".format(sSta_code)
    eSingle_data = open(sFile_path, "w", encoding="utf-8")

# Write the title
    sName_lat = dData["aName"]["lat"]
    sName_cyr = dData["aName"]["cyr"]
    sAll = "    {0}\n    {1}\n".format(sName_lat, sName_cyr)
    sAll += "----------\n"

    # Add the timestamp
    xNow = datetime.datetime.now()
    sAll += "Pretty print information was generated on {0}\n".format(xNow)

# Identifiation information
    sAll += "----------\n"
    sAll += "my_id: {0}\n".format(dData["my_id"])

# Type and sub_type information
    sLvl = dData["level"]
    sLong = ""
    sLvl_info = ""
    if sLvl == "Int'l":
        sLong = "International"
        sLvl_info = "['0V9'->'0Q1']"
    elif sLvl == "Nat'l":
        sLong = "National / Inter-Provincial"
        sLvl_info = "['V'->'L']"
    elif sLvl == "Prov.":
        sLong = "Provincial / Inter-District"
        sLvl_info = "['GY'->'VA']"
    elif sLvl == "Dist.":
        sLong = "District / Inter-County"
        sLvl_info = "['GYN'->'GY0']"
    elif sLvl == "Cnty.":
        sLong = "County / Inter-Municipal"
        sLvl_info = "['GYN-2'->'GYN-0']"
    elif sLvl == "Muni.":
        sLong = "Municipal / Intra-Municipal"
        sLvl_info = "['VAA-0A'->'VAA-0B']"
    else:
        pass

    sAll += "----------\n"
    sTxt = "Type: {0} {1}: {2}\n"
    sTxt = sTxt.format(sLong, dData["type"], dData["sub_type"])
    sAll += sTxt

    sAll += "Route example: {0}\n".format(sLvl_info)

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
        sAll += sTxt.format(aArea["val"], aArea["uom"])

    else:
        sAll +=  ">   No map declared\n"

# Services:
    lServices = dData["lServices"]
    sAll += "----------\n"
    sAll += "Services: \n"

    cDest = db.destinations(ccTremb)    # To get the names of the villages.
    for sServed in lServices:
        aName = misc.verify_geo_code(sServed, cDest)    # Fetches the names.
        sTxt = ">   [{0}] {1} / {2}\n"
        sAll += sTxt.format(sServed, aName["lat"], aName["cyr"])

    if len(lServices) < 1:
        sAll += ">   N/A\n"

# Warehouse:
    lWarehouse = dData["lWarehouse"]
    sAll += "----------\n"
    sAll += "Loading zones: {0}\n".format(dData["iLoading_zones"])

    sAll += "Resources transported:\n"
    for dResource in lWarehouse:
        sName = dResource["resource"]
        fQty = dResource["weekly_output"]
        sUnits = dResource["units"]
        sAll += ">   {0}: {1}{2}\n".format(sName, fQty, sUnits)

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

STATIONS SUB-MENU (S):
.:  Exit
1:  Add a station/port
2:  View all stations
3:  View single element
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
            add_station(ccTremb)
        elif sInput == "2":          # All the stations
            view_all(ccTremb)
        elif sInput == "3":         # View single
            view_single(ccTremb)
        elif sInput == "4":         # Formats the little bit of data
            pretty_print_single(ccTremb)
