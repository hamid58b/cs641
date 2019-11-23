import ast
import inspect
import time
import logging

from distributions import Discrete, Distribution


def f_phi(f, E_s, phi, *args):
    r = f(*args)
    # Check phi for the estimates and update the distributions
    # Create psi by replacing all of the expected values in phi with the estimates from the new distributions
    # Evaluate psi with the new estimates and determine true or false
    # Check if this evaluation is false and above k threshold then throw an error
    # else return

    return r


class PhiVisitor(ast.NodeVisitor):
    def __init__(self, distributions):
        self.pr_func_start = False
        self.expr = None
        self.distributions = distributions

    def visit_Name(self, node):
        if node.id in self.distributions:
            return self.distributions[node.id]
        return self.generic_visit(node)

    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        distributions = self.generic_visit(node)
        if distributions is not None and len(distributions) == 3:
            left = distributions[0]
            right = distributions[2]
            if isinstance(left, Discrete):
                left = (left == True)
            if isinstance(right, Discrete):
                right = (right == False)
            if right == 0:
                return float("inf")
            if isinstance(node.op, ast.BitOr):
                return (left + right) / right
            elif isinstance(node.op, ast.BitAnd):
                return left + right
            elif isinstance(node.op, ast.Div):
                return left / right
        return None

    def visit_Compare(self, node):
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        op = node.ops[0]
        if isinstance(op, ast.Gt):
            return left > right
        elif isinstance(op, ast.GtE):
            return left >= right
        elif isinstance(op, ast.Lt):
            return left < right
        elif isinstance(op, ast.LtE):
            return left <= right
        elif isinstance(op, ast.Eq):
            return left == right
        return None

    def visit_Call(self, node):
        if node.func.id == 'pr':
            self.pr_func_start = True
            random_variable = self.visit(node.args[0])
            self.pr_func_start = False
            return random_variable
        return None

    def generic_visit(self, node):
        returns = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        returns.append(self.visit(item))
            elif isinstance(value, ast.AST):
                returns.append(self.visit(value))
        if len(returns) == 0:
            return None
        if len(returns) == 1:
            return returns[0]
        return returns


class specdomain(object):
    # phi is the fairness assertion
    def __init__(self, phi, popModel, log_level=logging.WARNING):
        self.phi_str = phi
        self.popModel = popModel
        self.count = 0
        self.logger = logging.getLogger("SpecDomain")
        self.logger.setLevel(log_level)
        self.logger.addHandler(logging.StreamHandler())


    def __call__(self, func):
        self.func_name = func.__name__
        self.func_args = inspect.getfullargspec(func)
        self.logger.debug("Analyzing " + self.func_name + " with parameters: " + str(self.func_args.args))
        self.distributions = {self.func_name: Discrete()}
        for i in range(len(self.popModel)):
            self.distributions[self.func_args.args[i]] = self.popModel[i]

        self.phi_ast_node = ast.parse(self.phi_str)
        self.visitor = PhiVisitor(self.distributions)


        # func is the hire function
        # run domain knowledge (popModel) here on func (hire)
        # check if domain knowledge satisfies phi, if not throw error
        # run FairSquare with hire and popModel and report any errors
        # Update count of samples taken

        def wrap(*args, **kwargs):
            # Check if args falls within popModel, if so call func and return

            # Call the original transformed function in @spec which will do all of the phi calculations
            # Add aggregate arguments to distributions
            r = func(*args, **kwargs)
            self.count += 1
            self.distributions[self.func_name].append(r)
            #TODO: Aggregate argument data and update if necessary
            uEval = self.visitor.visit(self.phi_ast_node)

            return r

        return wrap
