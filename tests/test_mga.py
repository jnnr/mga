import os
import sys

import pandas as pd

from oemof.tools import logger
from oemof.tools import economics
from oemof import solph

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))
import mga


def create_model():
    date_time_index = pd.date_range("1/1/2012", periods=3, freq="H")

    energysystem = solph.EnergySystem(timeindex=date_time_index)

    # Read data file
    full_filename = os.path.join(here, "..", "storage_investment.csv")
    data = pd.read_csv(full_filename, sep=",")

    price_gas = 0.04

    # If the period is one year the equivalent periodical costs (epc) of an
    # investment are equal to the annuity. Use oemof's economic tools.
    epc_wind = economics.annuity(capex=1000, n=20, wacc=0.05)
    epc_storage = economics.annuity(capex=1000, n=20, wacc=0.05)

    ##########################################################################
    # Create oemof objects
    ##########################################################################

    # create natural gas bus
    bgas = solph.Bus(label="natural_gas")

    # create electricity bus
    bel = solph.Bus(label="electricity")

    energysystem.add(bgas, bel)

    # create source object representing the natural gas commodity (annual limit)
    gas_resource = solph.Source(
        label="rgas", outputs={bgas: solph.Flow(variable_costs=price_gas)}
    )

    # create fixed source object representing wind power plants
    wind = solph.Source(
        label="wind",
        outputs={
            bel: solph.Flow(
                fix=data["wind"], investment=solph.Investment(ep_costs=epc_wind)
            )
        },
    )

    # create simple sink object representing the electrical demand
    demand = solph.Sink(
        label="demand",
        inputs={bel: solph.Flow(fix=data["demand_el"], nominal_value=1)},
    )

    # create simple transformer object representing a gas power plant
    pp_gas = solph.Transformer(
        label="pp_gas",
        inputs={bgas: solph.Flow()},
        outputs={bel: solph.Flow(nominal_value=10e10, variable_costs=0)},
        conversion_factors={bel: 0.58},
    )

    # create storage object representing a battery
    storage = solph.components.GenericStorage(
        label="storage",
        inputs={bel: solph.Flow(variable_costs=0.0001)},
        outputs={bel: solph.Flow()},
        loss_rate=0.00,
        initial_storage_level=0,
        invest_relation_input_capacity=1 / 6,
        invest_relation_output_capacity=1 / 6,
        inflow_conversion_factor=1,
        outflow_conversion_factor=0.8,
        investment=solph.Investment(ep_costs=epc_storage),
    )

    energysystem.add(gas_resource, wind, demand, pp_gas, storage)

    # initialise the operational model
    om = solph.Model(energysystem)

    return om


def test_add_max_cost_constraint():

    om = create_model()

    mga.add_max_cost_constraint(om, 100)

    # TODO: compare lp-files


def test_set_new_objective():

    om = create_model()

    def obj_expr():
        return 2

    mga.set_new_objective(om, obj_expr, sense='max')

    # TODO: compare lp-files
    assert om.objective.expr() == 2.0


def test_add_max_cost_objective():

    om = create_model()

    def obj_expr():
        return 2

    mga.add_max_cost_constraint(om, 100)

    mga.set_new_objective(om, obj_expr, sense='max')

    # TODO: compare lp-files
    print(om.max_cost.max_cost_rule.expr)


def test_permute_add_max_cost_objective():

    om = create_model()

    def obj_expr():
        return 2

    mga.set_new_objective(om, obj_expr, sense='max')

    mga.add_max_cost_constraint(om, 100)

    # TODO: compare lp-files
    print(om.max_cost.max_cost_rule.expr)


def test_set_obj_max_investflows():
    # TODO
    pass


def test_mga_max_cost():
    # TODO: Assert that the costs of mga are the optimal costs plus slack
    om = create_model()

    om.solve()

    print(om.objective.expr)

    #function() * (1+slack) == objective_value * (1 + slack)
