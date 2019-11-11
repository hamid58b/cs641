import ast
import inspect
import time

def f_phi(f, E_s, phi, *args):
    r = f(*args)
    # Check phi for the estimates and update the distributions
    # Create psi by replacing all of the expected values in phi with the estimates from the new distributions
    # Evaluate psi with the new estimates and determine true or false
    # Check if this evaluation is false and above k threshold then throw an error
    # else return

    return r


class specdomain(object):
    # phi is the fairness assertion
    def __init__(self, phi, popModel):
        self.phi = phi
        self.popModel = popModel
        self.count = 0

    def __call__(self, func):
        self.name = func.__name__
        # func is the hire function
        # run domain knowledge (popModel) here on func (hire)
        # check if domain knowledge satisfies phi, if not throw error
        # run FairSquare with hire and popModel and report any errors
        # Update count of samples taken

        def wrap(*args, **kwargs):
            # Check if args falls within popModel, if so call func and return

            # Call the original transformed function in @spec which will do all of the phi calculations
            # Add aggregate arguments to distributions
            self.count += 1
            return f_phi(func, self.popModel, self.phi, *args)

        return wrap


