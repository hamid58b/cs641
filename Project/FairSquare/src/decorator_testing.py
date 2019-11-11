
from decorators import *

# Deciding function that hires a person with these three parameters
from simulate import gaussian


# @spec("pr(hire | ethnicity) / pr(hire | not ethnicity) > 0.8")
@specdomain("pr(hire | ethnicity) / pr(hire | not ethnicity) > 0.8",
            (gaussian(25,100), gaussian(10,25), gaussian(0,100)))
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