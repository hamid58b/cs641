import ast
import inspect
import time
import logging

from distributions import Discrete, DataPointList


class FairnessAssertionError(RuntimeError):
    def __init__(self, func_name, phi, count):
        self.func_name = func_name
        self.phi = phi
        self.count = count

def _make_bin_op(op, left, right):
    if isinstance(op, ast.BitOr):
        return left | right
    elif isinstance(op, ast.BitAnd):
        return left & right
    elif isinstance(op, ast.Div):
        return left / right
    raise SyntaxError("Op " + str(op) + " not provided")

def _make_comp_op(op, left, right):
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
    raise SyntaxError("Op " + str(op) + " not provided")

def _make_filter_function(op, name, other):
    def comp_func(row):
        if name in row:
            return _make_comp_op(op, row[name], other)
    return comp_func

def _and_filter_functions(filter1, filter2):
    return lambda row: filter1(row) and filter2(row)

class PhiListVisitor(ast.NodeVisitor):

    def __init__(self, data_list):
        self.data_list = data_list
        self.in_pr_func = False

    def visit_Name(self, node):
        if node.id in self.data_list:
            return node.id
        return None

    def visit_Num(self, node):
        return node.n

    def visit_Call(self, node):
        if node.func.id == 'pr':
            self.in_pr_func = True
            random_variable = self.visit(node.args[0])
            if not isinstance(random_variable, (int, float)):
                random_variable = len(self.data_list(random_variable)) / len(self.data_list)
            self.in_pr_func = False
            return random_variable
        return None

    def visit_Compare(self, node):
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])
        if self.in_pr_func and left is not None and right is not None:
            if isinstance(left, str):
                return _make_filter_function(node.ops[0], left, right)
            elif isinstance(right, str):
                return _make_filter_function(node.ops[0], right, left)
        # print("Comparing: " + str(left) + " | " + str(right))
        return _make_comp_op(node.ops[0], left, right)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if self.in_pr_func:
            if isinstance(left, str):
                left = _make_filter_function(ast.Eq(), left, True)
            if isinstance(right, str):
                right = _make_filter_function(ast.Eq(), right, True)
            if isinstance(node.op, ast.BitAnd):
                return _and_filter_functions(left, right)
            elif isinstance(node.op, ast.BitOr):
                right_data = self.data_list(right)
                if len(right_data) == 0:
                    return 0
                left_data = right_data(left)
                return len(left_data) / len(right_data)

        if right == 0:
            return 0
        if isinstance(node.op, ast.Div):
            return left / right

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


class PhiDistVisitor(ast.NodeVisitor):
    def __init__(self, distributions):
        self.in_pr_func = False
        self.expr = None
        self.distributions = distributions

    def visit_Name(self, node):
        if node.id in self.distributions:
            return self.distributions[node.id]
        return self.visit(node)

    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if self.in_pr_func:
            if isinstance(left, Discrete):
                left = (left == True)
            if isinstance(right, Discrete):
                right = (right == True)
            if right == 0:
                return float("inf")
            if isinstance(node.op, ast.BitOr):
                return
            elif isinstance(node.op, ast.BitAnd):
                return left + right
            elif isinstance(node.op, ast.Div):
                return left / right
        return

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
            self.in_pr_func = True
            random_variable = self.visit(node.args[0])
            self.in_pr_func = False
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


class spec(object):
    def __init__(self, phi):
        self.phi_str = phi

    def __append_data_point(self, r, args):
        row = {self.func_name: r}
        for i in range(len(args)):
            row[self.func_args.args[i]] = args[i]
        self.data_list.append(row)

    def __f_phi__(self, func, args):
        r = func(*args)

        # Add aggregate arguments to updated distributions
        self.__append_data_point(r, args)

        # Update estimates for phi
        uEval = self.visitor.visit(self.phi_ast_node)

        # Check uEval estimate and with threshold
        # if not uEval and len(self.data_list) > 50:
        #     raise FairnessAssertionError(self.func_name, self.phi_str, len(self.data_list))
        return r


    def __call__(self, func):
        self.func_name = func.__name__
        self.func_args = inspect.getfullargspec(func)

        names = [self.func_name]
        for arg in self.func_args.args:
            names.append(arg)
        self.data_list = DataPointList(names)

        self.phi_ast_node = ast.parse(self.phi_str)
        self.visitor = PhiListVisitor(self.data_list)

        def wrap(*args, **kwargs):
            return self.__f_phi__(func, args)

        return wrap


class specdomain(object):
    # phi is the fairness assertion
    def __init__(self, phi, popModel, empirical_count=1000, proportion_within=0.8, log_level=logging.WARNING):
        self.phi_str = phi
        self.popModel = popModel
        self.count = 0
        self.empirical_count = empirical_count
        self.proportion_within = proportion_within
        self.logger = logging.getLogger("SpecDomain")
        self.logger.setLevel(log_level)
        self.logger.addHandler(logging.StreamHandler())

    def __append_data_point(self, r, args):
        row = {self.func_name: r}
        for i in range(len(args)):
            row[self.func_args.args[i]] = args[i]
        self.data_list.append(row)

    # Check phi for the estimates and update the distributions
    # Create psi by replacing all of the expected values in phi with the estimates from the new distributions
    # Evaluate psi with the new estimates and determine true or false
    # Check if this evaluation is false and above k threshold then throw an error
    # else return

    def __f_phi__(self, func, args, skip_check=False):
        r = func(*args)

        # Check if args are in the distribution list
        if not skip_check:
            inside_distributions = True
            for i in range(len(args)):
                a, b = self.data_list.confidence(self.func_args.args[i], self.proportion_within)
                if not (a < args[i] < b):
                    inside_distributions = False
                    # print("Arguement outside " + str(self.func_args.args[i]) + " : " + str(a) + " < " + str(
                    #     args[i]) + " < " + str(b))
                    break
                # else:
                #     print("Arguement inside " + str(self.func_args.args[i]) + " : " + str(a) + " < " + str(args[i]) + " < " + str(b))
            if inside_distributions:
                # self.logger.debug("Skipped run")
                return r

        # Add aggregate arguments to updated distributions
        self.distributions[self.func_name].append(r)
        self.__append_data_point(r, args)

        self.count += 1
        # Update estimates for phi
        uEval = self.visitor.visit(self.phi_ast_node)

        # Check uEval estimate and with threshold
        # if not uEval and self.count > 50:
        #     raise FairnessAssertionError(self.func_name, self.phi_str, self.count)
        return r

    def __call__(self, func):
        self.func_name = func.__name__
        self.func_args = inspect.getfullargspec(func)
        self.logger.debug("Spec domain function name: " + str(self.func_name))
        self.distributions = {self.func_name: Discrete()}
        self.logger.debug("Creating Distributions from arguments: " + str(self.func_args.args))
        for i in range(len(self.popModel)):
            self.distributions[self.func_args.args[i]] = self.popModel[i]

        names = [self.func_name]
        for arg in self.func_args.args:
            names.append(arg)
        self.data_list = DataPointList(names)

        self.logger.debug("Creating phi ast node of: " + self.phi_str)
        self.phi_ast_node = ast.parse(self.phi_str)
        self.visitor = PhiListVisitor(self.data_list)

        self.logger.debug("Default checking of " + str(100 * self.proportion_within) + "% of all values inside each parameter")

        # Run domain knowledge to gather domain about the set (Tune Hyperparameter)
        self.logger.debug("Starting of Empirical data gathering of " + str(self.empirical_count) + " iterations")
        start = time.time()
        for t in range(self.empirical_count):
            params = []
            for arg in self.func_args.args:
                params.append(self.distributions[arg]())
            self.__f_phi__(func, params, skip_check=True)

        self.logger.debug("End of Empirical data gathering " + str(time.time() - start))
        self.logger.debug("Normal distributions of parameters: ")
        for name, value in self.data_list.mean_variance.items():
            self.logger.debug("\t Name: " + str(name) + " Mean: " + str(value[0]) + " Variance: " + str(value[1]))


        # Wrap the function to be used when f is called
        def wrap(*args, **kwargs):
            return self.__f_phi__(func, args)

        return wrap
