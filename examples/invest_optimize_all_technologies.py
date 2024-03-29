# -*- coding: utf-8 -*-

"""
General description
-------------------
This example shows how to perform a capacity optimization for
an energy system with storage. The following energy system is modeled:

                input/output  bgas     bel
                     |          |        |       |
                     |          |        |       |
 wind(FixedSource)   |------------------>|       |
                     |          |        |       |
 pv(FixedSource)     |------------------>|       |
                     |          |        |       |
 gas_resource        |--------->|        |       |
 (Commodity)         |          |        |       |
                     |          |        |       |
 demand(Sink)        |<------------------|       |
                     |          |        |       |
                     |          |        |       |
 pp_gas(Transformer) |<---------|        |       |
                     |------------------>|       |
                     |          |        |       |
 storage(Storage)    |<------------------|       |
                     |------------------>|       |

The example exists in four variations. The following parameters describe
the main setting for the optimization variation 1:

    - optimize wind, pv, gas_resource and storage
    - set investment cost for wind, pv and storage
    - set gas price for kWh

    Results show an installation of wind and the use of the gas resource.
    A renewable energy share of 51% is achieved.

    Have a look at different parameter settings. There are four variations
    of this example in the same folder.

Data
----
storage_investment.csv

Installation requirements
-------------------------
This example requires the version v0.3.x of oemof. Install by:

    pip install 'oemof.solph>=0.4,<0.5'

"""

__copyright__ = "oemof developer group"
__license__ = "GPLv3"

###############################################################################
# Imports
###############################################################################

import logging
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
from oemof import solph
# Default logger of oemof
from oemof.tools import economics, logger

sys.path.append("../")
from mga.mga import solve_mga_sampling, print_invest

number_timesteps = 3

##########################################################################
# Initialize the energy system and read/calculate necessary parameters
##########################################################################

logger.define_logging()
logging.info("Initialize the energy system")
date_time_index = pd.date_range("1/1/2012", periods=number_timesteps, freq="H")

energysystem = solph.EnergySystem(timeindex=date_time_index)

# Read data file
full_filename = os.path.join(os.getcwd(), "storage_investment.csv")
data = pd.read_csv(full_filename, sep=",")

price_gas = 0.04

# If the period is one year the equivalent periodical costs (epc) of an
# investment are equal to the annuity. Use oemof's economic tools.
epc_wind = economics.annuity(capex=1200, n=25, wacc=0.05)  # Eur/kW
epc_pv = economics.annuity(capex=700, n=25, wacc=0.05)
epc_storage_energy = economics.annuity(capex=300, n=15, wacc=0.05)
epc_pp_gas = economics.annuity(capex=500, n=25, wacc=0.05)

##########################################################################
# Create oemof objects
##########################################################################

logging.info("Create oemof objects")
# create natural gas bus
bgas = solph.Bus(label="natural_gas")

# create electricity bus
bel = solph.Bus(label="electricity")

energysystem.add(bgas, bel)

# create excess component for the electricity bus to allow overproduction
excess = solph.Sink(label="excess_bel", inputs={bel: solph.Flow()})

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

# create fixed source object representing pv power plants
pv = solph.Source(
    label="pv",
    outputs={
        bel: solph.Flow(
            fix=data["pv"], investment=solph.Investment(ep_costs=epc_pv)
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
    outputs={bel: solph.Flow(investment=solph.Investment(ep_costs=epc_pp_gas), variable_costs=0)},
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
    investment=solph.Investment(ep_costs=epc_storage_energy),
)

energysystem.add(excess, gas_resource, wind, pv, demand, pp_gas, storage)

##########################################################################
# Optimise the energy system
##########################################################################

logging.info("Optimise the energy system")

# initialise the operational model
om = solph.Model(energysystem)

# if tee_switch is true solver messages will be displayed
logging.info("Solve the optimization problem")


class Postprocessor():
    def __init__(self):
        self.results = pd.DataFrame()

    def process_sample(self, model, sample_id):
            # process and collect
            results = model.results()

            results = solph.processing.convert_keys_to_strings(results)

            scalars = {key: value['scalars'] for key, value in results.items() if 'scalars' in value}

            invest = {key: value['invest'] for key, value in scalars.items() if 'invest' in value}

            invest = pd.Series(invest)

            # assign sample name
            invest.name = sample_id

            self.results = pd.concat([self.results, invest], 1)

            print(invest)


pproc = solve_mga_sampling(om, 0.20, labels=['wind', 'pv', 'storage'], postproc=Postprocessor())

results = pproc.results
results.index = pd.MultiIndex.from_tuples(results.index)

global_optimum = results['global_optimum']
mga_samples = results.drop('global_optimum', 1)

min_max = mga_samples.apply(lambda x: pd.Series([min(x), max(x)], index=['min', 'max']), 1)

fig, ax = plt.subplots()
global_optimum.plot(ax=ax, linestyle='', marker='*')
min_max.plot(ax=ax, linestyle='', marker='_', markersize='12')
plt.xticks(rotation=45)
plt.subplots_adjust(bottom=0.3)
plt.show()
