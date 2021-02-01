import pyomo.environ as po
import copy

def add_max_cost_constraint(model, max_cost):
    def max_cost_func(m):
        return model.objective <= max_cost

    max_cost_block = po.Block()

    max_cost_block.max_cost_rule = po.Constraint(rule=max_cost_func)

    model.add_component("max_cost", max_cost_block)

    return model


def set_new_objective(model):

    def obj_expr():
        # Hier will ich auf die Investflow invest variablen zugreifen, nach bestimmten sorten filtern und
        # die dann maximieren
        expr = 0

        for i, o in model.InvestmentFlow.CONVEX_INVESTFLOWS:
            expr += (
                model.InvestmentFlow.invest[i, o]
            )
            
            print(type(i))

        # Dies hier scheint nicht nötig zu sein? Wirft jedenfalls einen Fehler.
        #expr = po.Expression(expr)

        return expr

    model.objective = po.Objective(sense=po.maximize, expr=obj_expr())

    return model


def do_mga(om, slack):

    # get the value of the objective function
    objective_value = om.objective.expr()

    # make former objective a constraint + slack
    function = copy.deepcopy(om.objective.expr)

    max_cost = (1 + slack) * objective_value

    add_max_cost_constraint(om, max_cost)

    set_new_objective(om)

    om.write('/home/jann/Desktop/file.lp', io_options={"symbolic_solver_labels": True})

    om.solve(solver="cbc", solve_kwargs={"tee": True})

    print(om.objective.expr)

    print(function() * (1+slack))
    print(objective_value * (1 + slack))

    import sys; sys.exit()
