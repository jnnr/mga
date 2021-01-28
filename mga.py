



def do_mga(om, slack):
    import pyomo.environ as po
    import copy

    # get the value of the objective function
    objective_value = om.objective.expr()

    # make former objective a constraint + slack
    function = copy.deepcopy(om.objective.expr)

    def max_cost_func(m):
        return om.objective <= (1 + slack) * objective_value

    max_cost_block = po.Block()

    max_cost_block.max_cost_rule = po.Constraint(rule=max_cost_func)
    om.add_component("max_cost", max_cost_block)

    # Set new objective
    print(om.objective.expr())

    print(om.InvestmentFlow.CONVEX_INVESTFLOWS)

    def obj_expr():
        # Hier will ich auf die Investflow invest variablen zugreifen, nach bestimmten sorten filtern und
        # die dann maximieren
        expr = 0

        for i, o in om.InvestmentFlow.CONVEX_INVESTFLOWS:
            expr += (
                om.InvestmentFlow.invest[i, o]
            )
            
            print(type(i))

        # Dies hier scheint nicht nötig zu sein? Wirft jedenfalls einen Fehler.
        #expr = po.Expression(expr)

        return expr

    om.objective = po.Objective(sense=po.maximize, expr=obj_expr())

    om.write('/home/jann/Desktop/file.lp', io_options={"symbolic_solver_labels": True})

    om.solve(solver="cbc", solve_kwargs={"tee": True})

    print(om.objective.expr)
    print(om.objective.expr())
    om._add_objective()
    print(function() * (1+slack))
    print(om.objective)
    print(om.objective())

    import sys; sys.exit()
