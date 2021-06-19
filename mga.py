import copy

import pyomo.environ as po


def add_max_cost_constraint(model, max_cost):
    r"""
    Takes an instance of oemof.solph.Model and an upper
    bound to the current models objective function.

    Parameters
    ----------

    model : oemof.solph.Model
        Model to which the constraint should be added.

    max_cost : numeric
        Value of the upper bound on the objective.

    Returns
    -------
    model : oemof.solph.Model
        Model with extra constraint.
    """
    def max_cost_func(m):
        return model.objective <= max_cost

    max_cost_block = po.Block()

    max_cost_block.max_cost_rule = po.Constraint(rule=max_cost_func)

    model.add_component("max_cost", max_cost_block)

    return model


def set_new_objective(model, obj_expr, sense='max'):
    r"""
    Set a new objective to a model.

    Parameters
    ----------

    model : oemof.solph.Model
        Model for which the new objective should be set.

    obj_expr : func
        New objective.

    sense : po.maximize or po.minimize

    Returns
    -------
    model : oemof.solph.Model
        Model with new objective.
    """
    if sense == 'min':
        set_sense = po.minimize

    elif sense == 'max':
        set_sense = po.maximize

    else:
        raise ValueError("Sense has to be either 'min' or 'max'!")

    model.objective = po.Objective(sense=set_sense, expr=obj_expr())

    return model


def set_obj_max_investflows(model, condition):
    r"""
    Sets the new objective to maximize the investflows that match a
    condition.

    Parameters
    ----------

    model : oemof.solph.Model
        Model for which the new objective should be set.

    condition : func
        Condition to match.

    Returns
    -------
    model : oemof.solph.Model
        Model with new objective.
    """
    def maximize_invest_flows():
        r"""
        Maximize investflows that match the condition.
        """
        expr = 0

        for i, o in model.InvestmentFlow.CONVEX_INVESTFLOWS:
            if condition(i):
                expr += (
                    model.InvestmentFlow.invest[i, o]
                )

        return expr

    set_new_objective(model, maximize_invest_flows)

    return model


def do_mga(model, slack, condition):
    r"""
    Perform a modeling-to-generate-alternatives sampling.

    Parameters
    ----------
    model : oemof.solph.Model

    slack : numeric

    condition :
    """
    # get the value of the objective function
    objective_value = model.objective.expr()

    # define max cost as minimal cost plus some tolerance.
    max_cost = (1 + slack) * objective_value

    # set an upper bound on the cost
    add_max_cost_constraint(model, max_cost)

    # set a new objective
    set_obj_max_investflows(model, condition)

    return model
