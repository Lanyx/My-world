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
        print("\nInput needs to be a floating-point number")
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
        print("\nInput needs to be an integer number")
        return None

    # We got our float converted. Now do its compares.
    if (iTop_lim != None) and (iInput > iTop_lim):
        sTxt = "\nTop limit has been exceeded. Input: {0}; Lim: {1}"
        print(sTxt.format(iInput, iTop_lim))
        return None

    if (bNeg == False) and (iInput < 0):
        print("\nInput is negative, which is not allowed")
        return None

    return iInput

#-------------------------------------------------------------------------------
def get_binary(sTitle):
    """ Prints the sTitle on the screen, and the instruction to enter Y or N.
    Then the user is propted for an input.
    If the input is not a 'Y', 'y', 'N', 'n' a None is returned. Otherwise, a
    'Y' or 'N' is returned."""

    # Format the question: new line, question itself, new line, options.
    sTxt = "\n{0}\nEnter 'y' or 'n' (case insensitive)\n"
    print(sTxt.format(sTitle))
    sInput = input().upper()

    if (sInput != "Y") and (sInput != "N"):
        print("Invalid input for binary choice. Expected 'Y', 'y', 'N', or 'n'")
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
