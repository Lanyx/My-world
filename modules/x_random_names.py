import random

def add_soft_vowel(sLat_syl, sCyr_syl):
    """ Method appends a vowel to the end of the syllable. However, it is only
    called if the cyrillic syllable ends in a soft-sign (external validation).
    Returns both the modified syllables"""

    # Vowels to choose from. Note that the cyrillic and latin must line up.
    aExtra_cyr = ["я", "е", "ьи", "ё", "ю", "ьы", "яь", "еь"]
    aExtra_lat = ["a", "e",  "i", "o", "u",  "y",  "à",  "è"]

    # Drop any silent letters
    if sLat_syl[-1] == "å": sLat_syl = sLat_syl[:-1]
    if sCyr_syl[-1] == "ь": sCyr_syl = sCyr_syl[:-1]

    # Pick the vowel at random, giving each choice equal weight
    iNo_of_extras = len(aExtra_cyr)
    iChance = random.randrange(0, iNo_of_extras)

    #Append the chosen final sound to the syllable
    sCyr_syl += aExtra_cyr[iChance]
    sLat_syl += aExtra_lat[iChance]
    return sLat_syl, sCyr_syl

#-------------------------------------------------------------------------------
def add_hard_vowel(sLat_syl, sCyr_syl):
    """ Method appends a vowel sound to the end of the syllable. External
    validation is required to ensure that there is no soft-sign (ь) in the
    final position. Returns both modified syllables."""
    aExtra_cyr = ["а", "э",  "и", "о", "у",  "ы", "аь", "эь"]
    aExtra_lat = ["a", "e",  "i", "o", "u",  "y",  "à",  "è"]

    # Remove 'placeholders'
    if sLat_syl[-1] == "å": sLat_syl = sLat_syl[:-1]
    if sCyr_syl[-1] == "щ": sCyr_syl = sCyr_syl[:-1]
    if sCyr_syl[-1] == "ъ": sCyr_syl = sCyr_syl[:-1]

    # Pick the vowel at random
    iNo_of_extras = len(aExtra_cyr)
    iChance = random.randrange(0, iNo_of_extras)

    # Append the syllable
    sCyr_syl += aExtra_cyr[iChance]
    sLat_syl += aExtra_lat[iChance]
    return sLat_syl, sCyr_syl


#-------------------------------------------------------------------------------
def add_consonant(sLat_syl, sCyr_syl):
    """ Appends the syllables with a consonant. It is done to syllables
    starting with a cyrillic consonant."""
    # The cyrillic azbuka. (for reference only)
    # А, Б, В, Г, Д, Е, Ё, Ж, З, И, Й, К, Л, М, Н,
    # О, П, Р, С, Т, У, Ф, Х, Ц, Ч, Ш, Щ, Э, Ю, Я

    # The additional letters
    aCyr_extra = [
        "б", "в", "д", "дь", "ж", "з", "зь", "й", "к", "л", "ль", "м",
        "н", "нь", "п", "р", "с", "сь", "т", "ть", "ф", "х", "ц", "ч", "ш"]
    aLat_extra = [
        "b", "v", "d", "ð", "zþ", "z", "zç", "ï", "k", "w", "l", "m",
        "n", "ñ", "p", "r", "s", "sç", "t", "tç", "f", "h", "ts", "tþ", "sþ"]

    iNo_of_extras = len(aCyr_extra)

    for first in ["б", "в", "г", "д", "ж", "з", "й", "к", "л", "м",
                  "н", "п", "р", "с", "т", "ф", "х", "ц", "ч", "ш"]:
        if sCyr_syl[0] != first: continue

        # First character is a consonant. Now, verify that the second is a
        # non-iotated (not a "я", "е", "ё", "ю") vovel. (it is an arbitary rule)
        # We are trying ot avoid "bl-" --> "blm"; we would prefer "ba-" -> "bag"
        for second in ["а", "и", "о", "у", "э"]:
            if sCyr_syl[1] != second: continue
            iChoice = random.randrange(0, iNo_of_extras)

            # Append the consonant
            sCyr_syl += aCyr_extra[iChoice]
            sLat_syl += aLat_extra[iChoice]

    # Handle "iï" as a single glyph "ÿ"
        if(sLat_syl[-2:] == "iï"): sLat_syl = sLat_syl[:-2] + "ÿ"

    return sLat_syl, sCyr_syl


#-------------------------------------------------------------------------------
def rnd_syllable(aSyl_scheme = [2, 2, 3, 3, 4, 4]):
    """ Generates (mostly) pronouncable names, constructed from syllables. Some
    syllables are modified, and may practically exceed the number of syllables
    specified. Method takes an array of integers. Each integer in the array
    describes the number of syllables picked at random to form a word. You may
    have as many syllables as you need, and as many randomly generated words as
    you need. Method returns an array of dictionaries with the generated words.
    Each dictionary contains 'lat', 'cyr', 'debug_lat', 'debug_cyr' keys. Both
    Latin and Cyrillic versions are returned, with initial capitalization. The
    debug elements show which base syllables were originally chosen."""

# DATABASE FOR THE SYLLABLES
    import modules.x_database as db

    # Connect to the database
    ccTremb = db.connect()
    cRnd_syl = db.rnd_syl(ccTremb)
    iNo_of_syl = 0

    # Count the number of sylables by running the query.
    xParam = {}                                                    # All queries
    xRestr = {"_id":0, "idx":1}
    dQuery = cRnd_syl.find(xParam, xRestr)
    for x in dQuery:
        iNo_of_syl += 1

    if(False):
        print("Number of syllables is {0}".format(iNo_of_syl))
    # This is the array that we will eventually return. It will be filled with
    # data inside a loop.
    aWords = []

# GENERATE THE LIST
    for syl_cnt in aSyl_scheme:
        # Context breaking: we are about to build the individual word from
        # syllables picked and sometimes modified at random.
        sLat_word, sCyr_word = "", ""                         # Final result
        sLat_log, sCyr_log = "", ""                           # Unmodified picks

# GENERATE THE WORD
        # We have already picked the number of syllables that we want. In the
        # loop below, we 'assemble' the word made up of the number of syllables
        # specified.
        for x in range(syl_cnt):
            # Pick the syllable base at random
            rnd_idx = random.randrange(0, iNo_of_syl)
            xParam = {"idx":rnd_idx}
            xRestr = {"_id":0, "lat":1, "cyr":1}
            dQuery = cRnd_syl.find(xParam, xRestr)
            sLat_syl, sCyr_syl = "", ""

    # GENERATE THE SYLLABLE
            for y in dQuery:
                # We have our randomly selected syllable base. Now extract it
                # for further processing.
                sLat_syl += y["lat"]
                sCyr_syl += y["cyr"]

                # For the debugger to see what was the original syllable chosen
                # and how it was modified.
                sLat_log += sLat_syl + "-"
                sCyr_log += sCyr_syl + "-"

        # VCV: Add a trailing wowel (ab-) -> (abi)
                bCyr_vowel = False            # Avoid a compound logic construct
                for vowel in ["а", "э", "и", "о", "у", "ы"]:
                    if vowel == sCyr_syl[0]: bCyr_vowel = True

                # Do the modification (sometimes the syllables are left as is)
                iChance = random.randrange(0, 100)
                if iChance < 95 and bCyr_vowel == True:
                    if(sCyr_syl[-1] == "ь"):
                        # Cyrillic orthrography rules: promote soft-sign to
                        # iotated vowel ("я", "е", "ё", "ю")
                        sLat_syl, sCyr_syl = add_soft_vowel(sLat_syl, sCyr_syl)
                    else:
                        sLat_syl, sCyr_syl = add_hard_vowel(sLat_syl, sCyr_syl)

            # ELIMINATE DOUBLE VOWEL: (ada + abo != adaabo; ... = adabo)
                for last_vowel in ["a", "e", "i", "o", "u", "y", "à", "è", "ø"]:
                    # Note: I use 'continue' here as to avoid indetation.
                    # Rather reject the negative then accept the positive.

                    #We need more than one syllable for this to work
                    if len(sLat_word) == 0: continue

                    # Check if we end in the vowel. If we don't, then move to
                    # the next letter.
                    if last_vowel != sLat_word[-1]: continue

                    # Check if the syllable begins with the specified letter.
                    if sLat_word[-1] != sLat_syl[0]: continue

                    # All checks passed, we can drop the letter.
                    sLat_word = sLat_word[:-1]

                    # Issue with cyrillic: Consider "аля" + "ари".
                    # NOTE: Cyrillic drops the first letter of the new syllable
                    # in order to preserve any iotated vowels.
                    sCyr_syl = sCyr_syl[1:]

            # HARD-SIGN BEFORE IOTATED
                for first_vowel in ["е", "ё", "ю", "я"]:
                    # Negative rejection instead of positive accepting in use

                    #We need more than one syllable for this to work
                    if len(sLat_word) == 0: continue

                    # Move to the next letter if not found
                    if sCyr_syl[0] != first_vowel: continue

                    # letters below have both soft and hard forms.
                    for last_char in ["д", "з", "л", "н", "с", "т"]:
                        if sCyr_word[-1] != last_char : continue
                        # "Fix" the issue with the hard-sign
                        sCyr_word += "ъ"

            # Й BEFORE A VOWEL
                # Clusters like "йа", "йе", "йё"
                if len(sLat_word) > 0 and sCyr_word[-1] == "й":
                    # remove the 'й', only if the vowel needs to be iotated
                    if sCyr_syl[0] == "а":
                        sCyr_syl = "я" + sCyr_syl[1:]
                        sCyr_word = sCyr_word[:-1]

                    if sCyr_syl[0] == "э":
                        sCyr_syl = "е" + sCyr_syl[1:]
                        sCyr_word = sCyr_word[:-1]

                    if sCyr_syl[0] == "о":
                        sCyr_syl = "ё" + sCyr_syl[1:]
                        sCyr_word = sCyr_word[:-1]

                    if sCyr_syl[0] == "у":
                        sCyr_syl = "ю" + sCyr_syl[1:]
                        sCyr_word = sCyr_word[:-1]

            # COMPULSORY VOWEL
                # The 'å' indicate that a trailing vowel is needed to make the
                # syllable readable
                if sLat_syl[-1] == "å":
                    if sCyr_syl[-1] == "щ":
                        sLat_syl, sCyr_syl = add_hard_vowel(sLat_syl, sCyr_syl)
                    elif sCyr_syl[-1] == "ъ":
                        sLat_syl, sCyr_syl = add_hard_vowel(sLat_syl, sCyr_syl)
                    elif sCyr_syl[-1] == "ь":
                        sLat_syl, sCyr_syl = add_soft_vowel(sLat_syl, sCyr_syl)

                # LATIN SOFT-END (ñ, sç, tç, zç) / (нь, сь, ть, зь)
                iChance = random.randrange(0, 100)
                bBool = False
                bBool = bBool or sLat_syl[-1] == "ñ"  # One of the soft elements
                bBool = bBool or sLat_syl[-1] == "ç"  # The 'consonant' softener
                bBool = bBool and iChance < 75      # Chances of it being needed
                bBool = bBool and sCyr_syl[-1] == "ь"    # Kind of a 'check-sum'
                if bBool == True:
                    sLat_syl, sCyr_syl = add_soft_vowel(sLat_syl, sCyr_syl)

            # CV to CVC system.
                iChance = random.randrange(0, 100)
                if iChance < 2:
                    sLat_syl, sCyr_syl = add_consonant(sLat_syl, sCyr_syl)

            # End of query, picking a syllable
            sLat_word += sLat_syl
            sCyr_word += sCyr_syl

        # End of multi-syllable
        # Check that we are not ending the word on a hard-sign (ъ) or the silent
        #vletter (å)
            if sLat_word[-1] == "å": sLat_word = sLat_word[:-1]
            if sCyr_word[-1] == "ъ": sCyr_word = sCyr_word[:-1]

        sLat_word = sLat_word.capitalize()
        sCyr_word = sCyr_word.capitalize()

        dNew_entry = {
            "lat":sLat_word,
            "cyr":sCyr_word,
            "debug_lat":sLat_log,
            "debug_cyr":sCyr_log
        }

        aWords.append(dNew_entry)
    # End of various words
    return aWords

#-------------------------------------------------------------------------------
def pick_name_w_alt(iNo_of_names, cChosen_db):
    """
    Selects the name from the selected data base (either Male or Female
    databases. This code would be common to 'rnd_male_name' and
    'rnd_female_name'.
    """
    # Count the number of names in the data base.
    xParam = {}
    xRestr = {"_id":0, "idx":1}
    iNo_of_entries = cChosen_db.find(xParam, xRestr).count()

    # Build an array containing indexes from 0 to the maximum
    aiIndexes = []
    for i in range(iNo_of_entries):
        aiIndexes.append(i)

    # Generate the names
    aaNames = []
    for i in range(iNo_of_names):
        iNo_of_choices = len(aiIndexes)
        iRnd = random.randrange(0, iNo_of_choices)
        iIdx_chosen = aiIndexes[iRnd]   # Pick an index from the list
        aiIndexes.remove(iIdx_chosen)         # Remove from the list

    # Go into the database and pic the index
        xParam = {"idx":iIdx_chosen}
        xRestr = {"_id":0}
        dQuery = cChosen_db.find(xParam, xRestr)
        for x in dQuery:
            # See if there are alternative spellings available
            dNew_name = {}
            iLen_alt = len(x["aAlt"])
            if iLen_alt > 0:
                iRnd_alt = random.randint(0, iLen_alt)
                if iRnd_alt == 0:
                    dNew_name["lat"] = x["lat"]
                else:
                    iRnd_alt -= 1           # allow for indexing in aAlt
                    dNew_name["lat"] = x["aAlt"][iRnd_alt]
            else:
                dNew_name["lat"] = x["lat"]
            dNew_name["cyr"] = x["cyr"]
            aaNames.append(dNew_name)

    # Export the names.
    return aaNames

#-------------------------------------------------------------------------------
def pick_surname(iNo_of_names, cChosen_db):
    """
    Selects the name from the selected data base (either Static, dynamic or
    suffix databases.
    """
    # Count the number of names in the data base.
    xParam = {}
    xRestr = {"_id":0, "idx":1}
    iNo_of_entries = cChosen_db.find(xParam, xRestr).count()

    # Build an array containing indexes from 0 to the maximum
    aiIndexes = []
    for i in range(iNo_of_entries):
        aiIndexes.append(i)

    # Generate the names
    aaNames = []
    for i in range(iNo_of_names):
        iNo_of_choices = len(aiIndexes)
        iRnd = random.randrange(0, iNo_of_choices)
        iIdx_chosen = aiIndexes[iRnd]   # Pick an index from the list
        aiIndexes.remove(iIdx_chosen)         # Remove from the list

    # Go into the database and pic the index
        xParam = {"idx":iIdx_chosen}
        xRestr = {"_id":0}
        dQuery = cChosen_db.find(xParam, xRestr)
        for x in dQuery:
            # See if there are alternative spellings available
            dNew_name = {}
            dNew_name["lat"] = x["lat"]
            dNew_name["cyr"] = x["cyr"]
            aaNames.append(dNew_name)

    # Export the names.
    return aaNames


#-------------------------------------------------------------------------------
def rnd_male_name(iNo_of_names):
    """ Picks specified number of male names from the database at random """

# DATABASE FOR THE MALE NAMES
    import modules.x_database as db

    # Connect to the database
    ccTremb = db.connect()
    cChosen_db = db.rnd_man(ccTremb)
    aaNames = pick_name_w_alt(iNo_of_names, cChosen_db)
    return aaNames

#-------------------------------------------------------------------------------
def rnd_female_name(iNo_of_names):
    """ Picks specified number of female names from the database at random """

# DATABASE FOR THE MALE NAMES
    import modules.x_database as db

    # Connect to the database
    ccTremb = db.connect()
    cChosen_db = db.rnd_woman(ccTremb)
    aaNames = pick_name_w_alt(iNo_of_names, cChosen_db)
    return aaNames

#-------------------------------------------------------------------------------
def qRnd_static_surname(iNo_of_names):
    """ Picks specified number of static surnames from the database at random
    """

# DATABASE FOR THE MALE NAMES
    import modules.x_database as db

    # Connect to the database
    ccTremb = db.connect()
    cChosen_db = db.rnd_static_surname(ccTremb)
    aaNames = pick_surname(iNo_of_names, cChosen_db)
    return aaNames

#-------------------------------------------------------------------------------
def glue_surnames(aPrefix, aSuffix):
    """ Method joins the latin and cyrillic texts together. The Latin doesn't
    hold much gramatical drama, but the Cyrillic puts up a fight.

    /!\ NOTE /!\

    DO NOT GLUE MALE NAMES TO SUFFIXES: The problem can be demonstrated with
    the following example:
                        Paulski != Павэлъски
    Names are not transliterations, they are sometimes translated. Surnames
    must be transliterated.

    """
    sLat_prefix = aPrefix["lat"]
    sLat_suffix = aSuffix["lat"]
    sCyr_prefix = aPrefix["cyr"]
    sCyr_suffix = aSuffix["cyr"]

    # Add the hard sign if necessary
    if sCyr_suffix[0] in ["я", "е", "ё", "ю"]:
        if sCyr_prefix[-1] in ["н", "з", "л", "д", "с", "т"]:
            sCyr_suffix = "ъ" + sCyr_suffix

    # Don't duplicate the 's'
    if sLat_suffix[0] == "s" and sLat_prefix[-1] == "s":
        sLat_prefix = sLat_prefix[:-1]

    if sCyr_suffix[0] == "с" and sCyr_prefix[-1] == "с":
        sCyr_prefix = sCyr_prefix[:-1]

    # Remove the latin hard sign ("þ") if it is duplicated in the suffix.
    if len(sLat_suffix) > 1 and sLat_suffix[1] == "þ" and sLat_prefix[-1] == "þ":
        sLat_prefix = sLat_prefix[:-1]

    # Янушщштайн
    if sCyr_suffix[0] == "ш" and sCyr_prefix[-1] == "ш":
        sCyr_prefix = sCyr_prefix + "щ"

    aNew_name = {}
    aNew_name["lat"] = sLat_prefix + sLat_suffix
    aNew_name["cyr"] = sCyr_prefix + sCyr_suffix
    return aNew_name

#-------------------------------------------------------------------------------
def qRnd_dynamic_surname(iNo_of_names):
    """ Generates surnames where two lists are combined. Method will obtain a
    list of prefixes and a list of suffixes. It will then combine them to form
    a generated surname.
    """

# DATABASE FOR THE MALE NAMES
    import modules.x_database as db

    # Get the prefixes
    ccTremb = db.connect()
    cChosen_db = db.rnd_dynamic_surname(ccTremb)
    aaPrefix = pick_surname(iNo_of_names, cChosen_db)

    # Get the suffixes
    cChosen_db = db.rnd_suffix_surname(ccTremb)
    aaSuffix = pick_surname(iNo_of_names, cChosen_db)

    # Let the 'gluing' begin
    aaNames = []
    for x in range(iNo_of_names):
        aName = glue_surnames(aaPrefix[x], aaSuffix[x])
        aaNames.append(aName)

    return aaNames

#-------------------------------------------------------------------------------
def qRnd_male_surname(iNo_of_names):
    """ Generates a surname (in Latin only) based on a Male name. This method
    provides the name and the suffix. The user needs to manually join the two
    elements when entering the place name by hand. Also, the user would need
    to transliterate it to cyrillic.
    """

# DATABASE FOR THE MALE NAMES
    import modules.x_database as db

    # Get the prefixes
    aaPrefix = rnd_male_name(iNo_of_names)

    # Get the suffixes
    ccTremb = db.connect()
    cChosen_db = db.rnd_suffix_surname(ccTremb)
    aaSuffix = pick_surname(iNo_of_names, cChosen_db)

    # Let the 'gluing' begin
    aaNames = []
    for x in range(iNo_of_names):
        aName = {}
        aName["cyr"] = "-"      # For the user to transliterate
        sLat = "{0} + {1}".format(aaPrefix[x]["lat"], aaSuffix[x]["lat"])
        aName["lat"] = sLat
        aaNames.append(aName)
    return aaNames


#-------------------------------------------------------------------------------
def sub_menu():
    """ Generates random names either from personal names, surnames and almost
        pronouncable sylables"""

    sMenu = """
.:  Exit
1:  Generate syllable-based random names
2:  Generate Male-based names
3:  Generate Female-based names
4:  Generate Static surnames (Not derived from any other name)
5:  Generate Dynamic surnames (Combination of two lists)
6:  Generate Male-name based surname (Latin only)
    """

    bExit = False
    while bExit == False:
        print(sMenu)
        sInput = input().upper()

        # Exit
        if sInput == ".":
            bExit = True

        # Syllable based
        elif sInput == "1":
            aNames = rnd_syllable([2, 2, 2, 3, 3, 3])
            for x in aNames:
                sTxt = "{0} / {1}\t\t{2} / {3}"
                print(sTxt.format(
                    x["lat"],
                    x["cyr"],
                    x["debug_lat"],
                    x["debug_cyr"]))

        # Male based
        elif sInput == "2":
            aNames = rnd_male_name(6)
            for x in aNames:
                sTxt = "{0} / {1}"
                print(sTxt.format(x["lat"], x["cyr"]))

        # Female based
        elif sInput == "3":
            aNames = rnd_female_name(6)
            for x in aNames:
                sTxt = "{0} / {1}"
                print(sTxt.format(x["lat"], x["cyr"]))

        # Static surname
        elif sInput == "4":
            aNames = qRnd_static_surname(6)
            for x in aNames:
                sTxt = "{0} / {1}"
                print(sTxt.format(x["lat"], x["cyr"]))

        # Dynamic surname
        elif sInput == "5":
            aNames = qRnd_dynamic_surname(6)
            for x in aNames:
                sTxt = "{0} / {1}"
                print(sTxt.format(x["lat"], x["cyr"]))

        # Dynamic surname
        elif sInput == "6":
            aNames = qRnd_male_surname(6)
            for x in aNames:
                sTxt = "{0} / {1}"
                print(sTxt.format(x["lat"], x["cyr"]))
