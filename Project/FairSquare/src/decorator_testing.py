
from decorators import *

def phi(args, returnvalue):
    return True

# Deciding function that hires a person with these three parameters
@spec(phi)
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