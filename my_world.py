""" 'Grzeg's World' is a fictional world drawing assistance tool. It assists
you with the geo-political tasks. You draw your political divisions on the map;
you then enter them into this software. A name will be suggested prior to
storing it with MongoDB. Your name is entered in two writing systems, which are
UTF-8 encoded.

The software assumes 1930's technology by default: Hence there is no magic. If
you intend to use the software for your magic filled world, go ahead, I won't be
offended.

When you get down to your agricultural areas, you simply tell the software the
area on the map: 'Grzeg's World' will give you the number of workers needed for
that land. Those farm workers live in a village: The village has doctors,
policemen, fire-chiefs, teachers, ... those households will can be added
automatically to the village. Your agricultural village grows wheat, for
example. At 5 tons per hectare, the software does the yield calculation for
you. Your village with its fields, is grouped into a municipalitity. A group of
municipalities is called a 'County'.

Each county has a 'capital town', which itself is a municipalitity too. The
'capital town' handle the 'collective' elements of your agricultural villages.
Elements like a rail depo where the grain from the farms is shipped to other
parts of the country. There could also be a hospital in the town, where the
village only has a clinic. The capital town would have some small industrial
components: perhaps a flour mill, or a mechanic?

Counties are grouped into Distrcts. Districts are quite importaint cities. Each
District has its own capital too. Once again, more specialised services are
available there.

Districts are grouped into Provinces; Provinces are grouped into Countries;
Countries are grouped into the World.

Eariler I mentioned the 'capital town'. It is in a municipalitity: an urban
municipalitity. A municipalitity can be sub-divided into a maximum of 36
Sections. [... it seems like my 'suburbs' got lost in the system. Well, I
haven't tested this work in progress to that level yet!].

I mentioned the number '36' earlier on. Note that every division has a maximum
of 36 sub-divisions. This is due to the 'geo-code' (geographic coding system)
which uses a base-36 system. A base-36 system looks like this:
0 to 9 then A to Z.

Country, Provincial and District geo-codes are independent of each other. Below
the district, there is inheretance of the geo-code. A county with the code 'GYN'
is in the 'GY' district. As we get lower down the hierarchy, our code grows.
After 3 alpha-numeric characters, we introduce a hyphen to make it easier to
read.


This is the main file, and holds the main menu.

HUNGARIAN NOTATION:
In this software, I will endevour to use hungarian notation through out.
a: array / list [] / dictionary (inconsistency)
b: binary
c: database
d: dictionary
e: file
f: float
g:
h:
i: integer
j: json
k:
l: list (inconsistency)
m:
n:
o: object (instance of a class)
p:
q: function
r: set
s: string
t: tuple ()
u: time/date
v:
w:
x: Miscellaneous
y:
z: complex number

Y-plates: (Various government institutions)
YA: Airforce
YB:
YC:
YD:
YE: Education (ED0 to ED9, excluding ED4)
YF: Firefighting and rescue
YG: Governance including royal family
YH: Health-care
YI: Information: Libraries, Radio/Television, State-theatre, Post office
YJ: Justice departament
YK:
YL:
YM: Military
YN: Navy
YO:
YP: Police
YQ:
YR:
YS:
YT:
YU:
YV:
YW:
YX: Corrctional services (Jail)
YY:
YZ:
Y0:
Y1:
Y2:
Y3:
Y4:
Y5:
Y6:
Y7:
Y8:
Y9:
Y0:
"""

#-------------------------------------------------------------------------------
def mm_exclamation():
    """ The hard-coded syllables are copied over from Ruby. Python then saves
    them in the data-base. Male names, female names and surnames are moved
    over too. """
    import modules.x_import_data as imdata
    imdata.import_syllables()            # Syllables
    imdata.import_male_names()           # For names of men
    imdata.import_female_names()         # Names for women
    imdata.import_static_surnames()      # Surnames
    imdata.import_dynamic_surnames()     # Surnames
    imdata.import_suffix_surnames()      # Male name and dynamic conversion
    imdata.import_demographic_const()    # Demographic constants
    imdata.import_city_services()        # Constants for police, schooling, ...
    imdata.import_workplaces()           # Farms, Offices, Factories, Stations

#-------------------------------------------------------------------------------
def mm_at():
    """ Loads data from 'ruby_json/d_destinations.json' backup file. This file
    was generated externally (by Ruby, in the previous rendition of the
    program). Do this as a seperate file."""
    import modules.x_import_data as imdata
    print("Are you sure that you want to overwrite all the current data?" +
        "\nType in 'Yes' if you want to destroy what has been logged already")
    sInput = input()
    if sInput == "Yes":
        imdata.import_ruby_d()

#-------------------------------------------------------------------------------
def mm_hash():
    """ Exports data to a dpy_destinations.json file. This is a different
    system, as it will Python to import it directly."""
    import modules.x_import_data as imdata
    imdata.export_python_d()

#-------------------------------------------------------------------------------
def mm_star():
    """ Tests a concept (This is a scratch pad, or a place to fix mistakes) """
    import modules.x_database as db
    # Delete a single entry
    if False:
        xParam = {"my_id":"D00-0CN"}
        xRestr = {}
        ccTremb = db.connect()
        cDatabase = db.destinations(ccTremb)
        dQuery = cDatabase.delete_one(xParam, xRestr)
        print("Specified element deleted")

    # Delete an entire collection
    if False:
        ccTremb = db.connect()
        cRnd_man = db.rnd_suffix_surname(ccTremb)
        dQuery = cRnd_man.delete_many({})
        print(dQuery.deleted_count, " deleted items!")

    # Update an array
    if False:
        xParam = {"geo_code":"TJV"}                # Vaenesston district
        xNew_data = {"$set": {"aChildren" : [
        "D00-09I", "D00-09J", "D00-0CM", "D00-0CN", "D00-0CO",]}}                        # Prepare the update

        ccTremb = db.connect()
        cDest = db.destinations(ccTremb)
        dParent_query = cDest.update_one(xParam, xNew_data)

    # Update a bad complex value
    if False:
        dNew_data = {
            "tot_road":50,
            "aItemised":{
                "maize farm":50,
            }
        }

        xParam = {"my_id":"D00-01T"}
        xNew_data = {"$set": {"aVehicles" : dNew_data}}

        ccTremb = db.connect()
        cDb = db.destinations(ccTremb)
        dQuery = cDb.update_one(xParam, xNew_data)

    # Global change to the structure
    if False:
        dNew_data = {"status":"RFU"}

        xParam = {}
        xNew_data = {"$set": {"aSupply_workforce" : dNew_data}}

        ccTremb = db.connect()
        cDb = db.destinations(ccTremb)
        dQuery = cDb.update_many(xParam, xNew_data)

    # Update a bad simple value
    if False:
        dNew_data = "D00-09N"

        xParam = {"parent":"VB"}
        xNew_data = {"$set": {"parent" : dNew_data}}

        ccTremb = db.connect()
        cDb = db.destinations(ccTremb)
    #    dQuery = cDb.update_one(xParam, xNew_data)
        dQuery = cDb.update_many(xParam, xNew_data)


    # delete an element
    if False:
        xParam = {"geo_code":"GYG"}
        xNew_data = {"$unset": {"aDemogfx_item":0, "aWhs_item":0}}

        ccTremb = db.connect()
        cDb = db.destinations(ccTremb)
        dQuery = cDb.update_one(xParam, xNew_data)


#-------------------------------------------------------------------------------
def mm_ampersand():
    """ Manually read the database (Edit the function for results)"""
    import modules.x_misc as misc
    import modules.x_database as db

    # Work out a name of the file
    sFile_path = "Logs/db_read.txt"
    eDb_read = open(sFile_path, "w", encoding="utf-8")

    # Read all the geographic data
    if False:
        # Do the query
        xParam = {"geo_code":None}         # All queries
        xRestr = {"_id":0, "aName":1, "parent":1}
        ccTremb = db.connect()
        cDb_of_choice = db.destinations(ccTremb)
        dQuery = cDb_of_choice.find(xParam, xRestr)

    # Read all the factory data
    if True:
        # Do the query
        xParam = {}         # All queries
        xRestr = {"_id":0}
        ccTremb = db.connect()
        cDb_of_choice = db.workplaces_const(ccTremb)
        dQuery = cDb_of_choice.find(xParam, xRestr)


    for x in dQuery:
        print(x)
        eDb_read.write("{0}\n".format(x))
    eDb_read.close()

#-------------------------------------------------------------------------------
def mm_backtick():
    """ Generates random names """
    import modules.x_random_names as x_rnd
    x_rnd.sub_menu()

#-------------------------------------------------------------------------------
def mm_d():
    """ Destinations menu which deals with the areas declared on the map"""
    import modules.d_destinations as d_py
    d_py.sub_menu()

#-------------------------------------------------------------------------------
def main_menu():
    """ Reroutes the program according to functionality """
    sMain_menu = """
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          GRZEG'S WORLD / СВЯТ ГЖЭСЯ:
                                    MAIN MENU
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
.: Exit
!: Load 'constants' into the database.
@: Import data destinations data from Ruby
#: Export data (to .json for backup in the Python system)
*: Test a concept / Fix mistake (Editable)
&: Manually read the database (Editable)

`: Generate random names

D: Destinations (geographic areas on the map)

"""
    bExit = False
    while bExit == False:
        print(sMain_menu)
        sInput = input().upper()

    # User has made their choice. Now, act on it.
        # Exit
        if sInput == ".":
            bExit = True

        # Imports data for the random name system.
        elif sInput == "!":
            mm_exclamation()

        # Import data from .json file backup
        elif sInput == "@":
            mm_at()

        # Export data to .json file for backup
        elif sInput == "#":
            mm_hash()

        # Test a concept, or fix a mistake (Editable)
        elif sInput == "*":
            mm_star()

        # Manually read the database (Editable)
        elif sInput == "&":
            mm_ampersand()

        # Random names
        elif sInput == "`":
            mm_backtick()

        # Geographic destinations menu
        elif sInput == "D":
            mm_d()

        else:
            pass
    print("\nProgram ended normally")

main_menu()
