
from decorators import *
from distributions import *
import scipy.stats

# Deciding function that hires a person with these three parameters
# pr(a | b) = pr(a & b) pr(b)

# @spec("pr(hire | ethnicity) / pr(hire | not ethnicity) > 0.8")
# pr(hire == True)
# pr(a & b)
@specdomain("pr(hire | (ethnicity > 10)) / pr(hire | (ethnicity <= 10)) > 0.8",
            (Gaussian(25,100), Gaussian(10,25), Gaussian(0, 100)),
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

# print(hire(25, 10, 0))