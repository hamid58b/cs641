
from decorators import *
from distributions import *

domains = (Gaussian(25,100), Gaussian(10,25), Gaussian(0, 100))

@specdomain("pr(hire | (ethnicity > 10)) / pr(hire | (ethnicity <= 10)) > 0.8",
            domains,
            log_level=logging.DEBUG)
def hire(colRank, yExp, ethnicity):
    if ethnicity > 10:
        colRank = colRank + 5
    expRank = yExp - colRank

    if colRank <= 5:
        return True
    elif expRank > -5:
        return False
    else:
        return False

@spec("pr(h | (ethnicity > 10)) / pr(h | (ethnicity <= 10)) > 0.8")
def h(colRank, yExp, ethnicity):
    if ethnicity > 10:
        colRank = colRank + 5
    expRank = yExp - colRank

    if colRank <= 5:
        return True
    elif expRank > -5:
        return False
    else:
        return False


# Runtime Timings
print("Starting Spec Domain Time Test")
start = time.time()
for i in range(1000):
    colRank = domains[0]()
    yExp = domains[1]()
    ethnicity = domains[2]()
    hire(colRank, yExp, ethnicity)
print("Spec Domain: " + str(time.time() - start))


start = time.time()
print("Starting Spec Time Test")
for i in range(2000):
    colRank = domains[0]()
    yExp = domains[1]()
    ethnicity = domains[2]()
    h(colRank, yExp, ethnicity)
print("Spec: " + str(time.time() - start))
