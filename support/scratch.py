"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)

"""
import random

import simpy


RANDOM_SEED = 42
NEW_CUSTOMERS = 5  # Total number of customers
INTERVAL_CUSTOMERS = 10.0  # Generate new customers roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience


def source(env, number, interval, counter):
    """Source generates customers randomly"""
    for i in range(number):
        c = customer(env, 'Customer%02d' % i, counter, time_in_bank=12.0)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def customer(env, name, counter, time_in_bank):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    print('%7.4f %s: Here I am' % (arrive, name))

    with counter.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        # Wait for the counter or abort at the end of our tether
        results = yield req | env.timeout(patience)

        wait = env.now - arrive

        if req in results:
            # We got to the counter
            print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))

            tib = random.expovariate(1.0 / time_in_bank)
            yield env.timeout(tib)
            print('%7.4f %s: Finished' % (env.now, name))

        else:
            # We reneged
            print('%7.4f %s: RENEGED after %6.3f' % (env.now, name, wait))


# Setup and start the simulation
print('Bank renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
counter = simpy.Resource(env, capacity=1)
env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counter))
env.run()







def qTrains_azufi(oEnv):
    oR_sta_1 = simpy.Resource(oEnv, 4)      # Station 1 has 4 tracks
    oR_track_1 = simpy.Resource(oEnv, 1)    # Track 1 can hold 1 train
    oR_track_2 = simpy.Resource(oEnv, 1)    # Track 2 can hold 1 train
    oR_sta_2 = simpy.Resource(oEnv, 2)      # Station 2 can hold 2 trains

    req_s1 = oR_sta_1.request()             # Wait to be allowed to "spawn"
    yield req_s1
    print("[{0:>5}] VIR: Good Morning.".format(oEnv.now))
    yield oEnv.timeout(2)                    # Load pax
# STATION_1 --> TRACK_1
    print("[{0:>5}] VIR: Request T1.".format(oEnv.now))
    req_t1 = oR_track_1.request()     # Wait to enter track 2
    yield req_t1
    print("[{0:>5}] VIR: Cleared to T1.".format(oEnv.now))
    yield oEnv.timeout(1)                    # Transiton from station to track
    oR_sta_1.release(req_s1)                 # Transitoined off the station
    print("[{0:>5}] VIR: S1 vacant.".format(oEnv.now))
# TRACK 1
    yield oEnv.timeout(10)                   # Travel time
# TRACK_1 --> TRACK_2
    print("[{0:>5}] VIR: Request T2.".format(oEnv.now))
    req_t2 = oR_track_2.request()
    yield req_t2
    print("[{0:>5}] VIR: Cleared to T2.".format(oEnv.now))
    yield oEnv.timeout(1)                    # Transition time
    oR_track_1.release(req_t1)
    print("[{0:>5}] VIR: T1 vacant.".format(oEnv.now))
# TRACK_2
    yield oEnv.timeout(15)                   # Travel time
# TRACK_2 --> STATION_2
    print("[{0:>5}] VIR: Request S2.".format(oEnv.now))
    req_s2 = oR_sta_2.request()
    yield req_s2
    print("[{0:>5}] VIR: Cleared to S2.".format(oEnv.now))
    yield oEnv.timeout(1)                    # Transition time
    oR_track_2.release(req_t2)
    print("[{0:>5}] VIR: T2 vacant.".format(oEnv.now))

    print("\n[{0:>5}] VIR: At platform S2\n".format(oEnv.now))
# STATION_2 --> TRACK_2
    yield oEnv.timeout(30)
    print("[{0:>5}] VIR: Request T2".format(oEnv.now))
    req_t2_b = oR_track_2.request()
    yield req_t2_b
    print("[{0:>5}] VIR: Cleared to T2".format(oEnv.now))
    yield oEnv.timeout(1)
    oR_sta_2.release(req_s2)
    print("[{0:>5}] VIR: S2 Vacant".format(oEnv.now))


def run_trains_azufi(ccTremb):

    oEnv = simpy.Environment()          # Open the framework
    oEnv.process(qTrains_azufi(oEnv))
    oEnv.run(until=900)








# Access database
    cLine = db.lines(ccTremb)

# Verify that the database exists:
    cLine = db.lines(ccTremb)
    xParam = {"my_id":sK_code, "tag":"meta"}
    xRestr = {"_id":0}
    dQuery = cLine.find(xParam, xRestr)

    # Extract the data
    dMeta = ""
    for query in dQuery:
        dMeta = query       # Save data for further processing

    if dMeta == "":
        print("\n\aNo information available")
        return None
