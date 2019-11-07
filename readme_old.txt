README FILE FOR 'MY_WORLD'

THIS SOFTWARE IS A WORK IN PROGRESS. ALSO, THIS SOFTWARE WAS NOT BETA TESTED.

TL;DR:
------
This software is a personal project written by Grzegorz Wochlik. In its current
state, it concentrates on capturing geographic data. This geographic data is
converted to demographic data. Effectively, it calculates the population size
of the various points on the map.

SETUP INSTRUCTIONS:
-------------------
1.)     This software requires MongoDB. My database has been 'pulled' from the
        official site.
2.)     This software requires pymongo gem. I used the 'pip'-system to acquire
        it.
3.)     Once 'pymongo' and 'MongoDB' have been installed, from the command line
        run: 'python my_world.py'
4.)     Select '!'-option from the main menu. This will setup all the
        'constants' in the database.
5.)     Test the installation by selecting the '`'-option. This will take you
        to a sub-menu which generates random names.
6.)     All of the options in the sub-menu should produce random names.
        TAKE NOTE, that the names are in my own conlang (constructed language).
        See the appendix of the document on how to attempt to pronounce these
        names.
7.)     You may recover the backup of my data included in this system. This will
        give you access to all my data. The data may contain geographic names
        which have personal significance; some names have been chosen at random.

OPERATING INSTRUCTIONS: REGISERING A MAPPED AREA
---------------------------------------------------
I use IMSI TurboCad to draft my maps. TurboCad is a paid software, and their
data format is proprietary. I have tried to use the open standards like .dxf or
.dwg or .svg; however the loss of quality during the conversion is not
acceptable.
The software is independent from the drafting program. Data needs to be
transferred manually.
The Trembovicean (adjective to my fictional country) system is a strict
hierarchy. The hierarchy is hard-coded into the system: if you are mapping the
real world, you may have to get creative with your geographic divisions.

1.)     Draw the map in CAD

2.)     Add the nested political divisions. In my system, I have:
            World,                              (This is the ultimate ancestor)
            Country,
            Province,
            District,
            County,
            Municipality,
        However, there are still lower divisions. Those are used on a city-level
        maps.
        I draw my political divisions as a series of interlocking polygons. A
        filled polygon is easier to select afterwards. See the appendix on how I
        draw my maps.

3.)     In the 'Destinations' menu, Select 'M' as to add the details of your
        map. Simply follow the prompts.

4.)     Areas are added in order from highest to lowest hierarchy. In the
        example above, a 'District' is a child to 'Province'. The system needs
        the Province to be defined before the District.
        Conversely, 'Municipality' has a parent in 'County'.
        There is a chain of ancestry all the way to the 'world'. The 'world' is
        always created first on brand new installations. If you are using my
        backed up data, that step has been already done. Thought was given to
        expand to multi-planetary systems...
        I am including the 'live' data that I am working with for my personal
        system. You may recover this backup into MongoDB if you want the full
        extent of my data. I don't mind you playing with my data. My backup is
        kept off-line. Some geographic names have personal significance, others
        are semi-significant while others are purely random.
        NOTE that each parent can have a maximum of 36 children. This is due to
        the identification system called 'geo-code' More about that later on.
        Hence, a District may have a maximum of 36 counties. If there is more,
        then the District needs to be split into two. (This scenario has
        happened to me already)

        To add an area, Select the 'D' (Destinations Menu)

5.)     In your CAD package, select the area of interest on the map. You will
        need the drawings x, y co-ordinates of that object, as well as the
        objects area.

6.)     In the software, Select '1' to Add an area. There will be a series of
        prompts (mostly in English) to guide you through.
            The geo_code of the parent establishes the parent-child link. The
        identifier of the parent (not a geo-code) is registered with the child.
        Also the child knows who its parent is via the identifier. The input is
        case insensitive.
            Map selection is next. It gives you a choice of the registered maps.
        Map information is registered with the child. In this quasi-tutorial, I
        assume that a map has been selected.
            x, y and area parameters are entered in next from the map. All the
        units are in mm and square mm for the area. Other measurement systems
        will not yield correct results.
            Next prompt asks the user to select the geo-political level of the
        area being entered. The name in both English and Cyrpol are given.
        An example of the geo-code is also given. The fictional example and a
        real-world example is shown. Select 0 to 8 and press enter.
            Usually, larger areas up to Counites are '0': General.
        Municipalities can be Agricultural or even Military!
            Now we are ready to name our area. If you have a name in mind,
        select 'n' enter. This will take you to a prompt where you can type in
        the name of the area being registered in the Latin alphabet. Accented
        characters are welcome; If you are developing your own system, you are
        not obliged to comply with my language.
            The second prompt is the same name but translated or transliterated
        into Cyrillic. I never tested the effect of not entering the Cyrillic.
        To be save, enter a space. If you want to use other system (like Hindi,
        or Arabic you may do so. Note that the right-to-left systems were never
        tested. The database is configured for UTF-8 characters, hence I don't
        foresee any issues.

        Returning to the choice of a random name, select 'y' and enter.
        Currently, there are 15 choices: the first 10 are generated by randomly
        picking syllables. Some syllables are modified, where an extra vowel is
        added. Option 11 is a male name, option 12 is a female name. These act
        as inspiration for a 'St. Paul' (Capital of Minnesota) type of name.
        Option 13 is a static surname to inspire 'Smithfield', where 'Smith' is
        the randomly selected surname. Option 14 is a constructed surname.
        Option 15 is a surname which is constructed from a male name. For
        example, you could be presented with "Aaron + son" to make "Aaronson"
        Note that this is only for inspiration.
        Once you picked a name, a confirmation prompt follows. This allows you
        to reject the name and either pick again or enter the manual mode and
        type out the inspired name by hand.

        Once you have confirmed the name of the area, the next prompt asks if
        you have already decided on the geo-code. If you are doing a batch of
        registrations, it is recommended to select no. There is an option to
        review all the place-names and assign them appropriate geo-codes.
        Please read about the Geo-codes in the appendix.

        Software confirms that the area was added by giving you your chosen name
        (the Latin part) in a message. It cycles you back to the 'destinations'
        menu, where you can repeat this point for the next area.
        At this stage, I would change the color or texture or somehow mark on
        the map that the area has been captured.

7.)     Lets assume that you have completed your batch within the larger
        geographic area. Now, lets check that everything is OK. Lets start by
        checking that we did not accidentally assigned our county to the wrong
        district!

        a.) From the 'destinations sub-menu', select '2': View children.
        b.) Enter the parent geo-code. It is the same parent that you entered
            for every child entry.
        c.) The results are dispayed both on the screen and are written to a
            file. Look in the project directory, under 'Logs'
        d.) Open the file marked with the parent's geo-code.
        e.) The first item is the system identifier 'D00-0BM' for example.
        f.) Make sure that all the items are sequential. 'BZ' + 1 = 'C0', and
            'C9' + 1 = 'CA' (Base-36 system)
            [Oh, what irony: I was testing the instructions as I typed them.
            Guess what? one of my counties is missing! I accidentally assigned
            it to another district. To correct this mistake, I needed to
            manually modify the database of both the incorrect and the correct
            parent. The child also needed its parent to be manually changed in
            the database]
        g.) The next entry in the text file is the map reference, followed by
            the co-ordinates and paper area.
            On the screen, I just show the area in world units (hecares or
            square kilometers). Both systems merge, where I show "none". This
            is reserved for the Geo-code which we haven't assigned yet.
        h.) Verify that the names are correct. Also check for any duplicated
            names.

8.)     Navigate to the destinations sub-menu, then select 'G' to 'Assign
        geo-codes to children'.

9.)     Enter the geo-code of the parent

10.)    There is an option to assign the codes manually. We say 'y'; as it is
        customary for the 'capital' of the area to get a non-random code. Please
        see the geo-codes appendix for rules.

11.)    In the manual mode, there is an index on the left. The current geo-code
        is shown in the braces. The latin name of the place is next.

12.)    Select your capital from the list

13.)    A list of all the available geo-codes is presented next. Select the
        numeric index of the code you want to assign. Usually, but not always,
        the capital gets the code with '0' (Zero). All the other codes form
        around it.

14.)    You have the option of continuing picking the codes manually, or
        allowing the computer to randomly assign them. Choose 'n', for 'no more
        manual assignments'

15.)    View the 'children' to see who got what code!

16.)    Update the map with the codes and names. Use the x, y and a parameters
        to find the correct area on the map.



==============================
APPENDIX I: THE LANGUAGE USED
==============================


=================================
APPENDIX II: THE GEO-CODE SYSTEM
=================================

=================================
APPENDIX III: MAP DRAWING
=================================

=================================
APPENDIX IV: WRONG PARENT
=================================

I was testing my instructions by actually working on a live map. I just wrote
the instructions on how to check that all the children are present. There was
one missing! The sequence jumped one identifier code. Unfortunately, the code
to move a child between two parents has not been written yet. Hence, a manual
and painful operation needs to be done.
These instructions are written 'live' as I fix the missing child problem:

1.) From the destinations sub-menu, select 'E' to edit an entry. This will give
    you the child's current parent.
    In my case, the 'parent'-key has the entry 'VC'. This is not 100% right, but
    we know where to look. The parent is supposed to be 'VB' The parent is
    supposed to be an identifier ("D00-001") for example and not a geo-code.
2.) Press "CTRL+BREAK" to exit the editor. The abort function has not been yet
    written. You should be back at the C:\> prompt.
3.) Re-enter the software by typing in "python my_world.py". Go to the
    "destinations" menu (D) and select '4' for pretty print. Enter the geo-code
    of the incorrect parent hosting our child. In my case, it is "VC".
4.) Select '4' (Pretty print) again, and enter the code for the correct parent.
    In my case it is "VB".
5.) The easiest way to fix this is via the script. I would have to edit the
    "mm_star" method in the file 'my_world.py'. This particular function has
    been written with this type of a fix in mind.
6.) Lets remove the child first. In the "mm_star" function, there is a section
    where you can edit arrays. From the "d_VB_pretty.txt" (the pretty print of
    the bad parent) copy out the list of the children.
7.) Move the list of the children into that array, then delete the 'unwanted'
    child from the list.
9.) Change the 'xParam' dictionary to {"geo_code":"VC"}. This will do a database
    search on the geo-code.
10. NOTE THAT YOU ARE EDITING LIVE DATABASE DATA, SO DO BE CAREFUL.
11. Enable that element by setting it to True. Make sure that every other
    element is set to False
12. Double-check your work: make sure that you are overwriting the correct
    geo-code with the correct chidren.
13. Save 'my_world.py'
14. Exit and re-enter the software, without exiting the shell. You can either
    use "CTRL+BREAK", or use '.' if you are in the menu system.
15. After re-entry, enter "*" (star) from the main menu. This will run the
    little script that we have written.
16. Child has been removed from the bad parent. Press '.' to exit the software,
    but keep the shell active.
17. In the file 'my_world.py', change the geo-code to the correct parent. In my
    case, it is 'VB'.
18. Move the list of children from the "d_VB_pretty.txt" file to the array in
    "mm_star". We are using the same function that removed the child.
    Effectively, we are updating all the children at once.
19. Slot the child where it is supposed to be.
20. Apply quotes to all the children.
21. Save the file, and run the software in the shell. Once again, activate the
    changes by using the "*"-command.
22. Press "." to exit to the shell.
23. De-activate addition of the child by setting the guarding 'if' statement to
    False.
24. Activate the guarding 'if' statement where is says 'Update a bad simple
    value'. Since we did not assing a geo-code, we need to use the identifer.
25. Edit xNew_data to assing 'parent' with the identifier of the missing child.
26. Verify the changes by doing a pretty print on the 'bad parent'
