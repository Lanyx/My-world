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
    """ Defines a train as a moving vehilce along the map"""
    def __init__(self, name, type, len, ccTremb):
        self.end_of_trip = False    # Flag to let the iteratior know we are done
        self.name = name            # Name or code of the train
        self.type = type            # Commuter, pax, express, freight, military
        self.iLen = len             # Length of the train
        self.ccTremb = ccTremb      # Database pointer
        self.clock_tick = 1         # One second by default

        self.start = None           # Starting station
        self.end = None             # Ending station
        self.dStops = []            # Stations to be visited & time stopped
        self.dRoute = []            # TBD
        self.cur_line = None        # K00-001 (VA-FS) for example
        self.cur_dir = None         # direction loco points ("home" / "away")
        self.cur_instr = "RED"      # 3-char instrction or upcoming signal
        self.dist_head = None       # Distance of loco from "home" of the line
        self.dist_tail = None       # Distance of end of train
        self.v_train = 0.0          # Velocity in km/h, wrt loco direction
        self.v_target = 0.0         # Target velocity
        self.v_cruise = None        # What speed is allowed, assuming GRN signal
        self.acc_set = None         # Our mandated acceleration rate
        self.dec_set = None         # Our mandated deceleration rate
        self.v_max = None           # Our mandated speed limit
        self.uTime_start = None     # Time our journey has started
        self.eTrip_log = None       # Pointer to a .txt-file logging the Trip

    # This is a custom getter, since we have a custom setter.
    @property
    def cur_instr(self):
        return self.__cur_instr

    # This is our custom setter, as we need to take some action when the light
    # changes.



# TODO: THIS IS A WRONG APPROACH. WE NEED TO BE CALLED ONCE PER SECOND AND
# FIGURE OUT OUR STATUS FROM THERE. THIS NEEDS A REWRITE


    @cur_instr.setter
    def cur_instr(self, new_instr):
        """ Instructions need to be processed in here. 'GRN', for example needs
        to set the target velocity to the current cruise speed"""
        self.__cur_instr = new_instr
    # GREEN LIGHT: Cleared to proceed.
        if new_instr == "GRN":
        # STANDING START
            if self.v_train == 0 and self.v_target == 0:
                print("\n0 & 0\n")
            # We are stationary.
                # Cruising speed not yet set
                if self.v_cruise == None:
                # What is behind us depends on which way we are pointing.
                    sSign_type = ""                  # For scope breaking
                    if self.cur_dir == "away":
                        sSign_type = "speed_away"
                    elif self.cur_dir == "home":
                        sSign_type = "speed_home"
                    else:
                        sTxt = ("{0} has no direction set. Exiting")
                        sTxt = sTxt.format(self.name)
                        print(sTxt)
                        return None
                # Prepare for DB query
                    cLine = db.lines(self.ccTremb)   # Access database
                    xParam = {
                        "my_id":self.cur_line,
                        "dVal.item":"sign",
                        "dVal.type":"speed_away",
                        "dVal.km":{"$lte": self.dist_head},
                    }
                    xRestr = {"_id":0}
                    dQuery = cLine.find_one(xParam, xRestr)

                # Now set our speed limit.
                    v_lim = dQuery["dVal"]["xVal"]["val"]
                    self.v_cruise = misc.get_train("norm_pax", "cruise", v_lim)
                # Cruise speed obtained;
                self.v_target = self.v_cruise  #
                self.v_train = 0.01            # Accelerate from next iteration
                return True         # Nothing more to do here.

        # WE HAVE A TARGET SPEED TO KEEP UP TO.
            if self.v_target > 0:
                print("\n\av_target > 0\n")
                # for equations of motion:
                # v = u + at; s = ut + 1/2at**2
                loc_u = self.v_train / 3.6      # km/h -> m/s
                loc_v_tgt = self.v_target / 3.6 # km/h -> m/s
                loc_a = self.acc_set            # easier to read
                loc_t = self.clock_tick         # Easier to read

                # ACCELERATE
                if self.v_train < self.v_target:
                    # v = u + at; # s = ut + 1/2at**2

                    # Get the target in m/s, as not to overshoot. The last
                    # iteration before reaching target velocity will have a
                    # custom acceleration.

                    loc_v = loc_u + (loc_a * loc_t) # New velocity

                    # We would overshoot our speed at full acceleration.
                    if loc_v > loc_v_tgt:
                        loc_v = loc_v_tgt
                        # Now we need to calculate the acceleration as to calc
                        # distance moved. From v = u + at, we get (v - u)/t
                        loc_a = (loc_v - loc_u) / loc_t

                    # Move the train along the tracks
                    # s = ut + 0.5at**2
                    loc_s = loc_u * loc_t                  # No acc part
                    loc_s += 0.5 * loc_a * loc_t**2        # Accel part

                    # Which direction is the locomotive pointing?
                    if self.cur_dir == "home":      # Decresing milestones
                        loc_s *= -1                 # Move towards home
                    self.dist_head += loc_s         # Add distance in.
                    self.dist_tail += loc_s         # Move tail of train too.

                    # Save the speed and distances
                    self.v_train = loc_v * 3.6      # m/s -> km/h

                # BRAKE
                elif self.v_train < self.v_target:
                    pass

                else:
                    pass


        # TRAIN IN MOTION
            else:
                pass
        elif new_instr == "YEL":
            pass
        elif new_instr == "RED":
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
    oT_alf = Train("ALF", "norm_pax", 200, ccTremb)
    oT_alf.start = "VA"
    oT_alf.end = "FS"

    # Fill in the data manually at first
    dRoute = [
        {"line":"K00-001", "dir":"away", "from":0.2, "to":248.0}
        ]
    oT_alf.dRoute = dRoute
    oT_alf.cur_line = "K00-001"
    oT_alf.cur_dir = "away"
    oT_alf.dist_head = 0.3          # Station is at 0.2, train is 0.2 long
    oT_alf.dist_tail = 0.1
    oT_alf.acc_set = misc.get_train("norm_pax", "acc")
    oT_alf.dec_set = misc.get_train("norm_pax", "dec")
    oT_alf.v_max = misc.get_train("norm_pax", "v_max")


    # GOING ALL MANUAL.
    uNow = dt.datetime(1930, 1, 6, 8, 15, 30)

    for tick in range(10):
    # First step: Advance the clock
        uNow += dt.timedelta(seconds=1)
        sNow = uNow.strftime("%a %H:%M:%S")

        if tick == 3:
            oT_alf.cur_instr = "GRN"    	   # "Enable the train"

    # Print the train's result
        sTxt = "[{0}] '{1}': {2:_^.4} {3:5.1f}km/h <{4:6.2f}km>"
        sTxt = sTxt.format(sNow, oT_alf.name, oT_alf.cur_instr,
                            oT_alf.v_train, oT_alf.dist_head)
        print(sTxt, end='\r') # overwrite prev
        time.sleep(1)



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
