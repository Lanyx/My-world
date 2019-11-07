#-------------------------------------------------------------------------------
""" This file handles all the database methods """
#-------------------------------------------------------------------------------

import pymongo

#-------------------------------------------------------------------------------
def connect():
    """ Connects to the 'trembovice' database, and returns the hande to it.
        If there is no connection made, then a 'None' is returned """
    # Default connection parameters:
    xConnect = pymongo.MongoClient("mongodb://localhost:27017/")
    aDatabase_names = xConnect.list_database_names()

    # Verify that the database does exist.
    if "trembovice" in aDatabase_names:
        ccTremb = xConnect["trembovice"]
        return ccTremb
    else:
        print("Data base 'trembovice' does not exist! Returning")
        return None

#-------------------------------------------------------------------------------
def destinations(ccTremb):
    """ Selects the 'destinations' database which has the geographic areas
        stored in it. This is the main element of the system. These 'geographic
        areas' also hold a detailed break-down of the population"""
#    return ccTremb["destinations"]
    return ccTremb["dest_test"]


#-------------------------------------------------------------------------------
def factories(ccTremb):
    """ Selectes the 'factories' database which stores information about the
        field or factory. It holds information like what is grown or produced
        there; what are the labour demands; what are the vehicular demands."""
    return ccTremb["factories"]

#-------------------------------------------------------------------------------
def rnd_syl(ccTremb):
    """ Selects the 'rnd_syl' (Sylalables for random names) database.
        These are syllables (in the linguistic sense) which are pronouncable to
        an English / Polish speaker. They are written in adaptations of the
        Cyrillic and Latin scripts."""
    return ccTremb["rnd_syl"]

#-------------------------------------------------------------------------------
def rnd_man(ccTremb):
    """ Selects the 'rnd_man' (Male names for random names) database.
        These are masculine names which are pronouncable to an English / Polish
        speaker. They are written in adaptations of the Cyrillic and Latin
        scripts. Male names also form the base of some surnames"""
    return ccTremb["rnd_man"]

#-------------------------------------------------------------------------------
def rnd_woman(ccTremb):
    """ Selects the 'rnd_woman' (Female names for random names) database.
        These are feminine names which are pronouncable to an English / Polish
        speaker. They are written in adaptations of the Cyrillic and Latin
        scripts. Male names also form the base of some surnames"""
    return ccTremb["rnd_woman"]

#-------------------------------------------------------------------------------
def rnd_static_surname(ccTremb):
    """ Selects the 'rnd_static_surname' (Family names for random names)
        database. These are surnames names which are pronouncable to an
        English / Polish speaker. They are written in adaptations of the
        Cyrillic and Latin scripts. """
    return ccTremb["rnd_static_surname"]

#-------------------------------------------------------------------------------
def rnd_dynamic_surname(ccTremb):
    """ Selects the 'rnd_dynamic_surname' (Family names construction for random
        names) database. These are surnames names which are pronouncable to an
        English / Polish speaker. They are written in adaptations of the
        Cyrillic and Latin scripts. """
    return ccTremb["rnd_dynamic_surname"]

#-------------------------------------------------------------------------------
def rnd_suffix_surname(ccTremb):
    """ Selects the 'rnd_suffix_surname' (Family name construction for
        random names) database. These are surnames names which are
        pronouncable to an English / Polish speaker. They are written in
        adaptations of the Cyrillic and Latin scripts. """
    return ccTremb["rnd_suffix_surname"]

#-------------------------------------------------------------------------------
def demogfx_const(ccTremb):
    """ Selects the 'demogfx_const' (Constants for demographics) database.
        These hold editable values pertaining to the population """
    return ccTremb["demogfx_const"]

#-------------------------------------------------------------------------------
def city_services_const(ccTremb):
    """ Selects the 'city_services_const' (Constants for services like schools,
    police, clinics) database. """
    return ccTremb["city_services_const"]

#-------------------------------------------------------------------------------
def workplaces_const(ccTremb):
    """ Selects the 'workplaces_const' (Constants for workforce consumers like
    wheat farms, car factories, district hospital, bed and breakfast..."""
    return ccTremb["workplaces_const"]


#-------------------------------------------------------------------------------
def maps_db(ccTremb):
    """ Selects the 'maps' database. This is a reference to the maps drawn in a
        CAD program. This data is transferred to the actual entry where it is
        supplemented with the x, y and area components
        (quoted in 'mm' and 'mm2')"""
    return ccTremb["maps"]