import ast
import inspect
import time


class spec(object):
    #TODO: Specify confidence interval???? as a new specification
    #phi is a boolean function with args and return function as input
    def __init__(self, phi):
        self.phi = phi
        self.distributions = []

    # Add aggregate arguments to distributions
    def _update_distributions(self, args):
        for i in range(len(args)):
            if self.distributions[i] is None:
                self.distributions[i] = []
            self.distributions[i].append(args[i])

    def _mean_and_std_distributions(self):
        means = []
        stds = []
        for distribution in self.distributions:
            total = 0
            for v in distribution:
                total += v
            means.append(total / len(distribution))



    def __call__(self, func):
        # Happens on the definition of the decorator
        ast_node = ast.parse(inspect.findsource(func))

        def wrap(*args, **kwargs):

            self._update_distributions(args)

            returnvalue = func(*args, **kwargs)
            if self.phi(args, returnvalue):
                return returnvalue
            else:
                raise ValueError("Fairness Violation")
        return wrap


class specdomain(object):
    # phi is a boolean function with args and return function as input
    def __init__(self, phi, domainknowledge):
        self.phi = phi
        self.domainknowledge = domainknowledge

    def __call__(self, func):
        # Happens on the definition of the decorator
        ast_node = ast.parse(inspect.findsource(func))
        # run domain knowledge here on function
        def wrap(*args, **kwargs):
            # Add aggregate arguements to distributions
            returnvalue = func(*args, **kwargs)
            # check if arguments fall into domainknowledge if so return without calling phi else run solver to check phi
            if self.phi(args, returnvalue):
                return returnvalue
            else:
                raise ValueError("Fairness Violation")

        return wrap

def timer(func):

    def inner(*args, **kwargs):
        start = time.time()

        returnvalue = func(*args, **kwargs)

        print("Time of Function: " + str(time.time() - start))
        return returnvalue
    return inner

