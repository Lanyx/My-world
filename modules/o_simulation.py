"""
This is the simulation menu. This allows the SimPy module to 'play' on our
'lines'. I will use it to calculate a train schedule.
"""

import modules.x_database as db
import modules.x_misc as misc
import datetime as dt
import time

# import simpy
import math

#-------------------------------------------------------------------------------
# -. Run database trains
#-------------------------------------------------------------------------------
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Train:
    """ Defines a train as a moving vehilce along the map. To initialise, give
    The name of the train service,
    What type it is ('norm_pax', 'fast_pax', 'freight', 'military'),
    The lenght of the train in meters,
    pointer to the main database,
    List of stations visited, including the initial and final station, as their
        geocodes."""

    def __init__(self, name, type, len, ccTremb, dStops):
    # Basic parameters
        self.status = "Running"     # Flag to let the iteratior know we are done
        self.name = name            # Name or code of the train
        self.type = type            # Commuter, pax, express, freight, military
        self.train_Len = len        # Length of the train
        self.ccTremb = ccTremb      # Database pointer
        self.clock_tick = 1         # One second by default
        self.cur_instr = "RED"      # By default, we wait for TTC for clearance

    # Train details
        self.train_acc = None       # Standard acceleration for this train type
        self.train_dec = None       # Std. braking for this train
        self.v_max = None           # Top speed of our train

        # Get the particular train's acceleration, deceleration and top speed
        self.train_acc = misc.get_train(self.type, "acc")
        self.train_dec = misc.get_train(self.type, "dec")
        self.v_max = misc.get_train(self.type, "v_max")

    # Route details
        self.rte_stop_ptr = 1       # Points to the next station
        self.rte_dStops = dStops    # Stations visited and how long
        self.rte_cur_line_ptr = None# Points to the current line
        self.rte_dLines = []        # The route in terms of lines
            # dLines: [{"line":"K00-001", "dir":"away", "from":0.2, "to":248.0}]
    # TODO: Manually calculate the

    # Next speed limit:
        self.next_v_lim_km = None   # Next speed limit at milestione
        self.next_v_lim_val = None  # Value of the next speed limit

    # Next station
        self.next_sta_km = None     # Mile stone
        self.next_sta_geo = None    # geocode of next station

    # Train position
        self.s_loco = None          # km from beginning of current line
        self.s_tail = None          # position of the tail of the train on line
        self.v_train = 0            # Current train velocity
        self.v_cruise = 0           # Current cruise speed
        self.v_spd_lim = 0          # Current speed limit

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_dir(self):
        """ Helper function to sort out if we must add or subtract from the
        milestones"""
        ptr = self.rte_cur_line_ptr # Which line am I on? (If just changed lines
            # then look back at the new host)
        dir = self.rte_dLines[ptr]["dir"]
        return dir

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set_v_cruise(self):
        """ Method gets a new cruising speed by looking at previous
        speed limit"""
        sSign_type = ""             # For context breaking

        # Get the sign in the correct direction
        dir = self.get_dir()
        if dir == "away":
            sSign_type = "speed_away"
        elif dir == "home":
            sSign_type = "speed_home"
        else:
            self.status == "confused"   # Invalid sign
            return None
            # TODO: add to trip log the error

        # Do the database query
        cLine = db.lines(self.ccTremb)   # Access database
        ptr = self.rte_cur_line_ptr
        xParam = {
            "my_id":self.rte_dLines[ptr]["line"],
            "dVal.item":"sign",
            "dVal.type":"speed_away",
            "dVal.km":{"$lte": self.s_loco},
        }
        xRestr = {"_id":0}
        dQuery = cLine.find(xParam, xRestr)         # Find all
        dQuery.sort("dVal.km")                      # sort by km
        dLimit = dQuery[0]                          # Pick the closest

    # Now set our speed limit.
        v_lim = dLimit["dVal"]["xVal"]["val"]
        self.v_cruise = misc.get_train(self.type, "cruise", v_lim)

    # Output our action:
        return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def accelerate(self):
        """ Increase the train's speed and position to achieve the cruising
        velocity, one 'click' at a time"""
        # v = u + at (Equation of linear motion):
        # s = ut + 0.5at**2 (Change in position)
        u = self.v_train / 3.6      # Vel. at begin of second in m/s
        a = self.train_acc          # acceleration in m/s/s
        t = self.clock_tick         # time interval in seconds

    # Calculate velocity:
        v = u + a*t                 # Vel. at end of time period in m/s

    # Check that we don't exceed the cruising speed. I don't want to oscilate
    # the speed by accelerate-decelerate.
        v_c = self.v_cruise / 3.6   # convert to m/s
        if v > v_c:
            v = v_c                 # We need to match the cruising speed
            # v = u + at, a = (v - u)/t. We need a custom acceleration
            a = (v - u) / t         # will be used in displacement

        self.v_train = v * 3.6      # Save the final velocity

    # Calculate the change in displacement of the train
        s = t * (u + 0.5 * a * t)   # Factor out one 't'
        s = s / 1000.0              # Convert to km

    # Figure out if we are adding to or subtracting from the milestones.
        dir = self.get_dir()
        if dir == "home":
            s *= -1                 # We will be subtracting
        self.s_loco = round(self.s_loco + s, 4)    # Locomotive end.
        self.s_tail = round(self.s_tail + s, 4)    # Back of the train (used to 'vacate')
        return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cruise(self):
        """ Increase the train's speed and position to achieve the cruising
        velocity, one 'click' at a time"""
        # v = u + (0)t => v = u => no change in velocity
        # s = ut + 0.5(0)t**2 => s = ut => Advance s.
        u = self.v_train / 3.6      # Vel. at begin of second in m/s
        t = self.clock_tick         # time interval in seconds

    # Calculate the change in displacement of the train
        s = u * t
        s = s / 1000.0              # Convert to km

    # Figure out if we are adding to or subtracting from the milestones.
        dir = self.get_dir()
        if dir == "home":
            s *= -1                 # We will be subtracting
        self.s_loco = round(self.s_loco + s, 4)    # Locomotive end.
        self.s_tail = round(self.s_tail + s, 4)    # Back of the train (used to 'vacate')

        sTxt = "u = {0:3.1f}, t = {1:3.1f}, s = {2:3.4f}"
        sTxt = sTxt.format(u, t, s)
        if False: print(sTxt)
        return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def decelerate(self):
        """ Increase the train's speed and position to achieve the cruising
        velocity, one 'click' at a time"""
        # v = u + at (Equation of linear motion):
        # s = ut + 0.5at**2 (Change in position)
        u = self.v_train / 3.6      # Vel. at begin of second in m/s
        a = -1 * self.train_dec     # deceleration in m/s/s
        t = self.clock_tick         # time interval in seconds

    # Calculate velocity:
        v = u + a*t                 # Vel. at end of time period in m/s

    # Check that we don't exceed the cruising speed. I don't want to oscilate
    # the speed by accelerate-decelerate.
        v_c = self.v_cruise / 3.6   # convert to m/s
        if v < v_c:
            v = v_c                 # We need to match the cruising speed
            # v = u + at, a = (v - u)/t. We need a custom acceleration
            a = (v - u) / t         # will be used in displacement

        self.v_train = v * 3.6      # Save the final velocity

    # Calculate the change in displacement of the train
        s = t * (u + 0.5 * a * t)   # Factor out one 't'
        s = s / 1000.0              # Convert to km

    # Figure out if we are adding to or subtracting from the milestones.
        dir = self.get_dir()
        if dir == "home":
            s *= -1                 # We will be subtracting
        self.s_loco = round(self.s_loco + s, 4)    # Locomotive end.
        self.s_tail = round(self.s_tail + s, 4)    # Back of the train (used to 'vacate')

        return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def find_next_speed_lim(self):
        """ Method looks ahead in the database for an upcoming speed limit"""
        # Get the sign in the correct direction
        sSign_type = ""             # For context breaking
        dir = self.get_dir()
        xIneq = None
        if dir == "away":
            sSign_type = "speed_away"
            xIneq = "$gt"
        else:
            sSign_type = "speed_home"
            xIneq = "$lt"

        # Do the database query
        cLine = db.lines(self.ccTremb)   # Access database
        ptr = self.rte_cur_line_ptr
        xParam = {
            "my_id":self.rte_dLines[ptr]["line"],
            "dVal.item":"sign",
            "dVal.type":"speed_away",
            "dVal.km":{xIneq: self.s_loco}, # TODO: The upper limit
        }
        xRestr = {"_id":0}
        dQuery = cLine.find(xParam, xRestr)         # Find oll of them
        dQuery.sort("dVal.km")                      # sort by km
        dLimit = dQuery[0]                          # pick the nearest one
    # Now set our speed limit.
        self.next_v_lim_val  = dLimit["dVal"]["xVal"]["val"]
        self.next_v_lim_km = dLimit["dVal"]["km"]
        return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check_next_speed_lim(self):
        """
        Method has the next speed limit saved in its variables. it compares it
        against its position. If the next limit is higher than our current
        speed, we accelerate behind the sign.
        If we need to slow down, we must slow down ahead of the sign.
        """
        # Is the next speed limit defined?
        if self.next_v_lim_km == None:
            self.find_next_speed_lim()

        # Distance to the next speed limit
        s_to_lim = self.next_v_lim_km - self.s_loco
        dir = self.get_dir()
        if dir == "home":
            s_to_lim *= -1

    # LIMIT IS HIGHER
        if self.next_v_lim_val >= self.v_train:
            if s_to_lim < 0:                # We overshot the higher S.L. sign
                self.v_cruise = misc.get_train(self.type, "cruise",
                                                self.next_v_lim_val)
                self.find_next_speed_lim()      # Generate the next one.
            return True

    # SLOW DOWN FOR NEW SPEED LIMIT
        v_new_cruise = 30                   # Emergency mode, fail safe
        lim = self.next_v_lim_val
        v_new_cruise = misc.get_train(self.type, "cruise", lim)

        # We got our cruising speed. Calculate our distance needed to slow down
        # over. If we are at that distance, instruct train to slow down.
        # v**2 = u**2 + 2as => s = (v**2 - u**2) / 2a
        v = v_new_cruise / 3.6          # Final vel; Convert to m/s
        u = self.v_train / 3.6          # Initial vel, Convert to m/s
        a = self.train_dec * -1         # deceleration, in m/s*2

        # Calculate the distance
        s = (v**2 - u**2) / (2*a)       # Distance needed to decelerate over
        s = s / 1000                    # convert to km.
        if s_to_lim < s:                # We will just overshoot the new limit.
            self.v_cruise = v_new_cruise    # Set the new cruising speed.

        # We crossed the limit. Setup for the next one.
        if s_to_lim < 0:
            self.find_next_speed_lim()
        return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def find_next_station(self):
        """ Method looks ahead in the database for an upcoming station limit"""
        # Get the sign in the correct direction
        sSign_type = ""             # For context breaking
        dir = self.get_dir()
        xIneq = None
        if dir == "away":
            xIneq = "$gt"
        else:
            xIneq = "$lt"

        # Do the database query
        cLine = db.lines(self.ccTremb)   # Access database
        ptr = self.rte_cur_line_ptr
        xParam = {
            "my_id":self.rte_dLines[ptr]["line"],
            "dVal.item":"station",
            "dVal.type":"geo_code",
            "dVal.km":{xIneq: self.s_loco},
        }
        xRestr = {"_id":0}
        dQuery = cLine.find(xParam, xRestr)         # Find oll of them
        dQuery.sort("dVal.km")                      # sort by km
        dLimit = dQuery[0]                          # pick the nearest one
    # Now set our speed limit.
        self.next_sta_geo  = dLimit["dVal"]["xVal"]["geo"]
        self.next_sta_km = dLimit["dVal"]["km"]
        return True


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def report_check_point(self):
        """
        Method reports on passing a checkpoints like stations.
        """
        self.find_next_station()

#===============================================================================
    def operate(self):
        """
        This is the main operation element of the train. This is called in the
        loop, and everything happens from here."""
    # PROGRAM IN CRUISE SPEED :
        if self.cur_instr == "GRN":
            if self.v_cruise == 0:
                self.set_v_cruise()                     # current speed limit
                self.find_next_speed_lim()              # Next speed limit
                return True

            # We are allowed to move
            if self.v_cruise > 0:
                # Train's technical speed limit (v_max) beats posted limit.
                # A freight train will go 80km/h in a 120km/h zone.
                if self.v_cruise > self.v_max:
                    self.v_cruise = self.v_max

                # See if we need to add speed
                if self.v_train < self.v_cruise:
                    self.accelerate()

                # Cruising within 0.1km/h of the desired speed. Direct == failed
                elif abs(self.v_train - self.v_cruise) < 0.1:
                    self.cruise()

                # Lower speed limit or a station
                elif self.v_train > self.v_cruise:
                    self.decelerate()

            # Look ahead for the next speed limit
            if self.v_train > 0:
                self.check_next_speed_lim()         # Do we need to slow down?
                self.report_check_point()

    # DO THE RED LIGHT INSTRUCTIONS
        elif self.cur_instr == "RED":
            pass

################################################################################
def run_trains(ccTremb):
    """
    The scope of this is difficult to describe. I just want to know the schedule
    of each train on the line. The ultimate goal is to determine the number of
    tracks and platforms needed for each station. SimPy is good, but I don't
    think it has been designed with over a thousand resources in mind.
    """

    # Setup the first train
    dStops = [{"sta": "VA", "time":None},
              {"sta": "FS", "time":None}]
    oVafs = Train("VA-FS", "norm_pax", 200, ccTremb, dStops)

    # Fill in the data manually at first
    dLines = [
        {"line":"K00-001", "dir":"away", "from":0.2, "to":248.0}
        ]

    oVafs.rte_dLines = dLines           # Manually find the route
    oVafs.rte_cur_line_ptr = 0          # Point to our line
    oVafs.s_loco = 0.3                  # Manual placement of locomotive
    oVafs.s_tail = 0.1                  # Manually place the tail of the train

    # To show stations we pass
    cDest = db.destinations(ccTremb)
    # GOING ALL MANUAL.
    uNow = dt.datetime(1930, 1, 6, 7, 59, 57)
    iRng = 192*60
    fSlp = 0.0

    for tick in range(iRng):
    # First step: Advance the clock
        uNow += dt.timedelta(seconds=1)
        sNow = uNow.strftime("%a %H:%M:%S")

    # Second step: TTC (Train Traffic Control) instructions
        if tick == 3:
            oVafs.cur_instr = "GRN"    	   # "Get the train going"

    # Third step: Move the trains
        oVafs.operate()                    # Main train operation

    # Print the train's result
        fLoco = oVafs.s_loco
        s_km = oVafs.next_v_lim_km
        if s_km == None:
            s_km = 0.00
        s_kmh = oVafs.next_v_lim_val
        if s_kmh == None:
            s_kmh = 0
        s_km = round(s_km - fLoco, 3)

        sSta = oVafs.next_sta_geo
        if sSta == None:
            sSta = ""
        fSta = oVafs.next_sta_km
        if fSta == None:
            fSta = 999.9

        if fSta - fLoco > 0.8:
            sName = ""
        else:
            if sSta != "":
                aNames = misc.verify_geo_code(sSta, cDest)
                sName = aNames["lat"]
                if len(sSta) <= 3:
                    sName = sName.upper()


        sTxt = ("[{0}] '{1}': {2:_^.4} {3:5.1f}km/h <{4:7.3f}km>" +
                " ({5:3d}) in {6:5.3}km {7:<.16}")
        sTxt = sTxt.format(sNow, oVafs.name, oVafs.cur_instr,
                            oVafs.v_train, fLoco, s_kmh, s_km, sName)
        print(sTxt) # overwrite prev
        time.sleep(fSlp)



#-------------------------------------------------------------------------------
# SUB-MENU
#-------------------------------------------------------------------------------
def sub_menu():
    """ Operates the simulator """
    ccTremb = db.connect()

    sSub_menu = """
SIMULATOR SUB-MENU (O):
.: Exit
X: Run Experiment (I don't know what I'm doing yet)
    """
# Go through the menu system.
    bExit = False
    while bExit == False:                            # loop until the user exits
        print(sSub_menu)
        sInput = input().upper()

        # Analise the user choice
        if sInput == ".":       # Exit
            bExit = True
        elif sInput == "X":     # Open new line
            run_trains(ccTremb)
