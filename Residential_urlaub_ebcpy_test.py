import os
import pathlib
import easygui as gui
import pandas as pd
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
# Imports from ebcpy
from ebcpy import DymolaAPI, TimeSeriesData, FMU_API
from ebcpy.utils.conversion import convert_tsd_to_modelica_txt

from teaser.logic.buildingobjects.buildingphysics.window import Window
from teaser.project import Project
from teaser.logic.buildingobjects.building import Building
from teaser.logic.buildingobjects.thermalzone import ThermalZone
from teaser.logic.buildingobjects.useconditions \
    import UseConditions
from teaser.logic.buildingobjects.buildingphysics.outerwall import OuterWall
from teaser.logic.buildingobjects.buildingphysics.innerwall import InnerWall
from teaser.logic.buildingobjects.buildingphysics.ceiling import Ceiling
from teaser.logic.buildingobjects.buildingphysics.floor import Floor
import teaser.logic.utilities as utilities
# from teaser.logic.buildingobjects.buildingphysics.layer import Layer
# from teaser.logic.buildingobjects.buildingphysics.material import Material


def main(
        aixlib_mo,
        teaser_mo,
        building_mo,
        savepath,
        result_file_name,
        cd=None,
        n_cpu=1,
        min_year_of_construction=None,
        max_year_of_construction=None,
        height_of_floors=None,
        with_ahu=None,
        residential_layout=None,
        internal_gains=None,
        with_heating=None,
        construction=None,
        with_plot=True,
):
    # General settings
    if cd is None:
        cd = pathlib.Path(__file__).parent.joinpath("results")

    # ######################### Simulation API Instantiation ##########################
    # %% Setup the Dymola-API:
    dym_api = DymolaAPI(
        model_name=building_mo,
        cd=cd,
        n_cpu=n_cpu,
        packages=[aixlib_mo, teaser_mo],
        show_window=True,
        n_restart=-1,
        equidistant_output=False,
        get_structural_parameters=True,
        # Only necessary if you need a specific dymola version
        dymola_path=(r'C:\Program Files\Dymola 2021')
        # dymola_version=None
    )

    ######################### Teaser ##########################
    prj = Project(load_data=True)
    prj.used_library_calc = 'AixLib',
    prj.number_of_elements_calc = 2
    prj.weather_file_path = utilities.get_full_path(
        os.path.join(
            "data",
            "input",
            "inputdata",
            "weatherdata",
            "DEU_BW_Mannheim_107290_TRY2010_12_Jahr_BBSR.mos"))

# ______________________________________________________________________________________________________________________________________________________________________________

    # Szenario
    scenario = 1  # 1 oder 2'
    weekend = 1  # 0 oder 1

     # Create a list of years of construction
    construction_years =[1900, 1925, 1950, 1962, 1970, 1980, 1992, 2000, 2003]

    # create a dictionary to map the areas to the years of construction
    area_construction_years = {
        75: construction_years[0],
        75: construction_years[1],
        68: construction_years[2],
        62: construction_years[3],
        67: construction_years[4],
        73: construction_years[5],
        75: construction_years[6],
        73: construction_years[7],
        75: construction_years[8],
        85: construction_years[9],
       }

    # create a loop to assign the years of construction to each area
    for area in building_model.thermal_zones:
        area.set_attribute('year_of_construction', area_construction_years[area.area])

    # Create a list of tuples with each leased area and corresponding year of construction
    year_leased_area = list(zip(years_of_construction, leased_areas))

    # loop over all years of construction and simulate each building
    for year, leased_area in year_leased_area:
        print(f"Creating building model for year {year} with leased area {leased_area}...")

        # Create the building model
        building = Building(
            net_leased_area=leased_area,
            year_of_construction=year,
            height_of_floors=height_of_floors,
            number_of_floors=number_of_floors,
            with_ahu=with_ahu,
            residential_layout=residential_layout,
            internal_gains=internal_gains,
            with_heating=with_heating,
            construction=construction,
            name=f"Building {year}_{leased_area}"
        )

        # Add a thermal zone to the building model
        zone = ThermalZone(
            name="ThermalZone",
            use_conditions=UseConditions(
                occupancy=occupancy,
                monday_schedule=monday_schedule,
                tuesday_schedule=tuesday_schedule)
        )
  # Run the simulation
        result = simulate_building(
            aixlib_mo=aixlib_mo,
            teaser_mo=teaser_mo,
            building=building,
            thermal_zones=[zone],
            cd=cd,
            n_cpu=n_cpu,
            savepath=savepath,
            result_file_name=result_file_name,
            with_plot=with_plot,
        )

        # Print the heating energy demand for the building
        print(f"Heating energy demand for Building {year}_{leased_area}: {result.heating_demand:.2f} kWh")
#
# Parameter Maximim-, Minimumwerte und Schrittgrößen. Bei festem Wert: Max = Min eingeben
# Anzahl Etagen
min_number_of_floors = 1
max_number_of_floors = 1
step_number_of_floors = 1

# Geschosshöhe
min_height_of_floors = 3.0
max_height_of_floors = 3.0
step_height_of_floors = .5

# AirHandlingUnit
both_ahu = False  # Modelle mit beiden Optionen? (an und aus)
with_ahu = False  # Falls nur mit einem -> Mit (true) oder ohne (false)?

# Struktur
both_layout = False  # Modelle mit beiden Optionen? (an und aus)
residential_layout = 0  # 0 -> compact; 1 -> elongated/complex

# Internal gains
internal_gains_all = False  # Modelle mit allen Optionen?
internal_gains = 1

# Heizung
both_heating = False  # Modelle mit beiden Optionen? (an und aus)
with_heating = True

#Bautyp
both_const = True #Modelle mit beiden Optionen? (an und aus)
construction = "tabula_retrofit"

# Urlaubswochen
holiday = [4, 5, 20, 21, 40, 41]

# ______________________________________________________________________________________________________________________________________________________________________________

usage = 'multi_family_house'
name = "3ZimKid"
method = 'tabula_de'

# ______________Zähler für die Schleifen______________
if internal_gains_all:
    internal_gains_help = 3
else:
    internal_gains_help = 1

if both_layout:
    layout_help = 2
else:
    layout_help = 1

if both_ahu:
    ahu_help = 2
else:
    ahu_help = 1

if both_heating:
    heating_help = 2
else:
    heating_help = 1

if both_const:
    const_help = 2
else:
    const_help = 1

zone0_M = []
zone1_M = []
zone2_M = []
zone3_M = []
zone4_M = []
zone0_H = []
zone1_H = []
zone2_H = []
zone3_H = []
zone4_H = []
zone0_P = []
zone1_P = []
zone2_P = []
zone3_P = []
zone4_P = []
y = 1
height_help = int((max_height_of_floors - min_height_of_floors) / step_height_of_floors) + 1
number_floors_help = int((max_number_of_floors - min_number_of_floors) / step_number_of_floors) + 1

# ___________________Schleifen_____________________
leased_area = min_leased_area
for x in range(area_help):

    year_of_construction = min_year_of_construction
    for x in range(year_help):

        number_of_floors = min_number_of_floors
        for x in range(number_floors_help):

            height_of_floors = min_height_of_floors
            for x in range(height_help):

                for x in range(ahu_help):

                    if both_layout:
                        residential_layout = 0
                    for x in range(layout_help):

                        if internal_gains_all:
                            internal_gains = 1
                        for x in range(internal_gains_help):

                            for x in range(heating_help):

                                if both_const:
                                    construction = "tabula_standard"
                                for x in range(const_help):

                                    prj.name = name + "_urlaub_scenario:" + str(scenario) + "_area:" + str(leased_area) + "_constructed:" + str(year_of_construction) + "_numberFloors:" + str(number_of_floors) + "_heightFloors:" + str(height_of_floors) + "_ahu:" + str(with_ahu) + "_layout:" + str(residential_layout) + "_internalGainsMode:" + str(internal_gains) + "_heating:" + str(with_heating) + "_constructiontyp:" + str(construction)
                                    W_G = prj.add_residential(
                                        method=method,
                                        usage=usage,
                                        name=name,
                                        year_of_construction=year_of_construction,
                                        number_of_floors=number_of_floors,
                                        height_of_floors=height_of_floors,
                                        net_leased_area=leased_area,
                                        with_ahu=with_ahu,
                                        residential_layout=residential_layout,
                                        internal_gains_mode=internal_gains,
                                        construction_type=construction
                                    )

                                    W_G.thermal_zones[0].use_conditions.machines = 1000 / (0.25 * leased_area)
                                    W_G.thermal_zones[1].use_conditions.machines = 1000 / (0.20 * leased_area)
                                    W_G.thermal_zones[2].use_conditions.machines = 1000 / (0.15 * leased_area)
                                    W_G.thermal_zones[3].use_conditions.machines = 1000 / (0.20 * leased_area)
                                    W_G.thermal_zones[4].use_conditions.machines = 1000 / (0.20 * leased_area)


                                    for x in range(53):
                                        if x in holiday:
                                            if scenario == 1 and weekend == 0 or scenario == 1 and weekend == 1:
                                                for y in range(7):
                                                    zone0_M.extend([0]*24)
                                                    zone1_M.extend([0.165]*24)
                                                    zone2_M.extend([0]*24)
                                                    zone3_M.extend([0]*24)
                                                    zone4_M.extend([0] * 24)
                                                    zone0_P.extend([0] * 24)
                                                    zone1_P.extend([0] * 24)
                                                    zone2_P.extend([0] * 24)
                                                    zone3_P.extend([0] * 24)
                                                    zone4_P.extend([0] * 24)
                                                    zone0_H.extend([288.15] * 24)
                                                    zone1_H.extend([288.15] * 24)
                                                    zone2_H.extend([288.15] * 24)
                                                    zone3_H.extend([288.15] * 24)
                                                    zone4_H.extend([288.15] * 24)

                                            elif scenario == 2 and weekend == 0 or scenario == 2 and weekend == 1:
                                                for y in range(7):
                                                    zone0_M.extend([0] * 24)
                                                    zone1_M.extend([0.165] * 24)
                                                    zone2_M.extend([0] * 24)
                                                    zone3_M.extend([0] * 24)
                                                    zone4_M.extend([0] * 24)
                                                    zone0_P.extend([0] * 24)
                                                    zone1_P.extend([0] * 24)
                                                    zone2_P.extend([0] * 24)
                                                    zone3_P.extend([0] * 24)
                                                    zone4_P.extend([0] * 24)
                                                    zone0_H.extend([288.15] * 24)
                                                    zone1_H.extend([288.15] * 24)
                                                    zone2_H.extend([288.15] * 24)
                                                    zone3_H.extend([288.15] * 24)
                                                    zone4_H.extend([288.15] * 24)
                                            else:
                                                print(
                                                    'Scenario ' + str(scenario) + ' nicht vorhanden. Kein Modell erstellt!')
                                                quit()
                                        else:
                                            if scenario == 1 and weekend == 0:
                                                for y in range(5):
                                                    zone0_M.extend([0,	0,	0,	0,	0,	0,	0,	0.06,	0.2376,	0.18,	0.18,	0.18,	0.18,	0.18,	0.18,	0.18,	0.18,	0.18,	0.18,	0.297,	0.297,	0.297,	0.2994,	0])
                                                    zone1_M.extend([0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.48,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.7004,	0.165,	0.165,	0.165,	0.165])
                                                    zone2_M.extend([0,	0,	0,	0,	0,	0,	0,	0,	0.005,	0,	0.005,	0,	0,	0,	0,	0,	0,	0.005,	0,	0,	0,	0,	0.03,	0])
                                                    zone3_M.extend([0,	0,	0,	0,	0,	0,	0.06,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0.06])
                                                    zone4_M.extend([0,	0,	0,	0,	0,	0,	0.06,	0,	0,	0,	0,	0,	0,	0,	0,	0.15,	0.15,	0.15,	0.15,	0,	0,	0,	0.06,	0])
                                                    zone0_P.extend(W_G.thermal_zones[0].use_conditions.persons_profile)
                                                    zone1_P.extend(W_G.thermal_zones[1].use_conditions.persons_profile)
                                                    zone2_P.extend(W_G.thermal_zones[2].use_conditions.persons_profile)
                                                    zone3_P.extend(W_G.thermal_zones[3].use_conditions.persons_profile)
                                                    zone4_P.extend(W_G.thermal_zones[4].use_conditions.persons_profile)
                                                    zone0_H.extend(W_G.thermal_zones[0].use_conditions.heating_profile)
                                                    zone1_H.extend(W_G.thermal_zones[1].use_conditions.heating_profile)
                                                    zone2_H.extend(W_G.thermal_zones[2].use_conditions.heating_profile)
                                                    zone3_H.extend(W_G.thermal_zones[3].use_conditions.heating_profile)
                                                    zone4_H.extend(W_G.thermal_zones[4].use_conditions.heating_profile)
                                                for y in range(5, 7):
                                                    zone0_M.extend([0]*24)
                                                    zone1_M.extend([0.165] * 24)
                                                    zone2_M.extend([0] * 24)
                                                    zone3_M.extend([0] * 24)
                                                    zone4_M.extend([0] * 24)
                                                    zone0_P.extend([0] * 24)
                                                    zone1_P.extend([0] * 24)
                                                    zone2_P.extend([0] * 24)
                                                    zone3_P.extend([0] * 24)
                                                    zone4_P.extend([0] * 24)
                                                    zone0_H.extend([288.15] * 24)
                                                    zone1_H.extend([288.15] * 24)
                                                    zone2_H.extend([288.15] * 24)
                                                    zone3_H.extend([288.15] * 24)
                                                    zone4_H.extend([288.15] * 24)
                                            elif scenario == 1 and weekend == 1:
                                                for y in range(5):
                                                    zone0_M.extend([0, 0, 0, 0, 0, 0, 0, 0.06, 0.2376, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.297, 0.297, 0.297, 0.2994, 0])
                                                    zone1_M.extend([0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.48, 0.165,0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.7004, 0.165, 0.165, 0.165, 0.165])
                                                    zone2_M.extend([0, 0, 0, 0, 0, 0, 0, 0, 0.005, 0, 0.005, 0, 0, 0, 0, 0, 0, 0.005, 0, 0, 0, 0, 0.03, 0])
                                                    zone3_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.06])
                                                    zone4_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0.15, 0.15, 0.15, 0.15, 0, 0, 0, 0.06, 0])
                                                    zone0_P.extend(W_G.thermal_zones[0].use_conditions.persons_profile)
                                                    zone1_P.extend(W_G.thermal_zones[1].use_conditions.persons_profile)
                                                    zone2_P.extend(W_G.thermal_zones[2].use_conditions.persons_profile)
                                                    zone3_P.extend(W_G.thermal_zones[3].use_conditions.persons_profile)
                                                    zone4_P.extend(W_G.thermal_zones[4].use_conditions.persons_profile)
                                                    zone0_H.extend(W_G.thermal_zones[0].use_conditions.heating_profile)
                                                    zone1_H.extend(W_G.thermal_zones[1].use_conditions.heating_profile)
                                                    zone2_H.extend(W_G.thermal_zones[2].use_conditions.heating_profile)
                                                    zone3_H.extend(W_G.thermal_zones[3].use_conditions.heating_profile)
                                                    zone4_H.extend(W_G.thermal_zones[4].use_conditions.heating_profile)
                                                for y in range(5, 7):
                                                    zone0_M.extend([0,	0,	0,	0,	0,	0,	0,	0.06,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0.255,	0,	0,	0.255,	0.255])
                                                    zone1_M.extend([0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.48,	0.165,	0.165,	0.165,	0.165,	0.165,	0.48,	0.165,	0.165,	0.165,	0.165,	0.165,	0.7004,	0.165,	0.165,	0.165,	0.165])
                                                    zone2_M.extend([0,	0,	0,	0,	0,	0,	0.03,	0,	0.005,	0,	0.005,	0,	0,	0,	0,	0,	0,	0.005,	0,	0,	0,	0,	0.03,	0])
                                                    zone3_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.06])
                                                    zone4_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0.15, 0.15, 0.15, 0.15, 0, 0, 0, 0.06, 0])
                                                    zone0_P.extend(W_G.thermal_zones[0].use_conditions.persons_profile)
                                                    zone1_P.extend(W_G.thermal_zones[1].use_conditions.persons_profile)
                                                    zone2_P.extend(W_G.thermal_zones[2].use_conditions.persons_profile)
                                                    zone3_P.extend(W_G.thermal_zones[3].use_conditions.persons_profile)
                                                    zone4_P.extend(W_G.thermal_zones[4].use_conditions.persons_profile)
                                                    zone0_H.extend(W_G.thermal_zones[0].use_conditions.heating_profile)
                                                    zone1_H.extend(W_G.thermal_zones[1].use_conditions.heating_profile)
                                                    zone2_H.extend(W_G.thermal_zones[2].use_conditions.heating_profile)
                                                    zone3_H.extend(W_G.thermal_zones[3].use_conditions.heating_profile)
                                                    zone4_H.extend(W_G.thermal_zones[4].use_conditions.heating_profile)
                                            elif scenario == 2 and weekend == 0:
                                                for y in range(5):
                                                    zone0_M.extend([0, 0, 0, 0, 0, 0, 0, 0.06, 0.2376, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.297, 0.297, 0.297, 0.2994, 0])
                                                    zone1_M.extend([0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.165,	0.48,	0.165,	0.165,	0.165,	0.165,	0.165,	0.48,	0.165,	0.165,	0.165,	0.165,	0.165,	0.7004,	0.165,	0.165,	0.165,	0.165])
                                                    zone2_M.extend([0, 0, 0, 0, 0, 0, 0, 0, 0.005, 0, 0.005, 0, 0, 0, 0, 0, 0, 0.005, 0, 0, 0, 0, 0.03, 0])
                                                    zone3_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.06])
                                                    zone4_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0.15, 0.15, 0.15, 0.15, 0, 0, 0, 0.06, 0])
                                                    zone0_P.extend(W_G.thermal_zones[0].use_conditions.persons_profile)
                                                    zone1_P.extend(W_G.thermal_zones[1].use_conditions.persons_profile)
                                                    zone2_P.extend(W_G.thermal_zones[2].use_conditions.persons_profile)
                                                    zone3_P.extend(W_G.thermal_zones[3].use_conditions.persons_profile)
                                                    zone4_P.extend(W_G.thermal_zones[4].use_conditions.persons_profile)
                                                    zone0_H.extend([294.15] * 24)
                                                    zone1_H.extend([294.15] * 24)
                                                    zone2_H.extend([294.15] * 24)
                                                    zone3_H.extend([294.15] * 24)
                                                    zone4_H.extend([294.15] * 24)
                                                for y in range(5, 7):
                                                    zone0_M.extend([0]*24)
                                                    zone1_M.extend([0.165] * 24)
                                                    zone2_M.extend([0] * 24)
                                                    zone3_M.extend([0] * 24)
                                                    zone4_M.extend([0] * 24)
                                                    zone0_P.extend([0] * 24)
                                                    zone1_P.extend([0] * 24)
                                                    zone2_P.extend([0] * 24)
                                                    zone3_P.extend([0] * 24)
                                                    zone4_P.extend([0] * 24)
                                                    zone0_H.extend([294.15] * 24)
                                                    zone1_H.extend([294.15] * 24)
                                                    zone2_H.extend([294.15] * 24)
                                                    zone3_H.extend([294.15] * 24)
                                                    zone4_H.extend([294.15] * 24)
                                            elif scenario == 2 and weekend == 1:
                                                for y in range(5):
                                                    zone0_M.extend([0, 0, 0, 0, 0, 0, 0, 0.06, 0.2376, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.297, 0.297, 0.297, 0.2994, 0])
                                                    zone1_M.extend([0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.48, 0.165, 0.165, 0.165, 0.165, 0.165, 0.48, 0.165, 0.165, 0.165, 0.165, 0.165, 0.7004, 0.165, 0.165, 0.165, 0.165])
                                                    zone2_M.extend([0, 0, 0, 0, 0, 0, 0, 0, 0.005, 0, 0.005, 0, 0, 0, 0, 0, 0, 0.005, 0, 0, 0, 0, 0.03, 0])
                                                    zone3_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.06])
                                                    zone4_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0.15, 0.15, 0.15,0.15, 0, 0, 0, 0.06, 0])
                                                    zone0_P.extend(W_G.thermal_zones[0].use_conditions.persons_profile)
                                                    zone1_P.extend(W_G.thermal_zones[1].use_conditions.persons_profile)
                                                    zone2_P.extend(W_G.thermal_zones[2].use_conditions.persons_profile)
                                                    zone3_P.extend(W_G.thermal_zones[3].use_conditions.persons_profile)
                                                    zone4_P.extend(W_G.thermal_zones[4].use_conditions.persons_profile)
                                                    zone0_H.extend([294.15] * 24)
                                                    zone1_H.extend([294.15] * 24)
                                                    zone2_H.extend([294.15] * 24)
                                                    zone3_H.extend([294.15] * 24)
                                                    zone4_H.extend([294.15] * 24)
                                                for y in range(5, 7):
                                                    zone0_M.extend([0, 0, 0, 0, 0, 0, 0, 0.06, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0.255, 0, 0, 0.255, 0.255])
                                                    zone1_M.extend([0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.165, 0.48, 0.165, 0.165, 0.165, 0.165, 0.165, 0.48, 0.165, 0.165, 0.165, 0.165, 0.165, 0.7004, 0.165, 0.165, 0.165, 0.165])
                                                    zone2_M.extend([0, 0, 0, 0, 0, 0, 0.03, 0, 0.005, 0, 0.005, 0, 0, 0, 0, 0, 0, 0.005, 0, 0, 0, 0, 0.03, 0])
                                                    zone3_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.06])
                                                    zone4_M.extend([0, 0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0.15, 0.15, 0.15, 0.15, 0, 0, 0, 0.06, 0])
                                                    zone0_P.extend(W_G.thermal_zones[0].use_conditions.persons_profile)
                                                    zone1_P.extend(W_G.thermal_zones[1].use_conditions.persons_profile)
                                                    zone2_P.extend(W_G.thermal_zones[2].use_conditions.persons_profile)
                                                    zone3_P.extend(W_G.thermal_zones[3].use_conditions.persons_profile)
                                                    zone4_P.extend(W_G.thermal_zones[4].use_conditions.persons_profile)
                                                    zone0_H.extend([294.15] * 24)
                                                    zone1_H.extend([294.15] * 24)
                                                    zone2_H.extend([294.15] * 24)
                                                    zone3_H.extend([294.15] * 24)
                                                    zone4_H.extend([294.15] * 24)
                                            else:
                                                print(
                                                    'Scenario ' + str(
                                                        scenario) + ' nicht vorhanden. Kein Modell erstellt!')
                                                quit()

                                    W_G.thermal_zones[0].use_conditions.machines_profile = zone0_M
                                    W_G.thermal_zones[1].use_conditions.machines_profile = zone1_M
                                    W_G.thermal_zones[2].use_conditions.machines_profile = zone2_M
                                    W_G.thermal_zones[3].use_conditions.machines_profile = zone3_M
                                    W_G.thermal_zones[4].use_conditions.machines_profile = zone4_M
                                    W_G.thermal_zones[0].use_conditions.persons_profile = zone0_P
                                    W_G.thermal_zones[1].use_conditions.persons_profile = zone1_P
                                    W_G.thermal_zones[2].use_conditions.persons_profile = zone2_P
                                    W_G.thermal_zones[3].use_conditions.persons_profile = zone3_P
                                    W_G.thermal_zones[4].use_conditions.persons_profile = zone4_P
                                    W_G.thermal_zones[0].use_conditions.heating_profile = zone0_H
                                    W_G.thermal_zones[1].use_conditions.heating_profile = zone1_H
                                    W_G.thermal_zones[2].use_conditions.heating_profile = zone2_H
                                    W_G.thermal_zones[3].use_conditions.heating_profile = zone3_H
                                    W_G.thermal_zones[4].use_conditions.heating_profile = zone4_H
                                    for x in range(4):
                                        W_G.thermal_zones[x].use_conditions.with_heating = with_heating


                                    prj.calc_all_buildings()
                                    prj.export_aixlib()

                                    model_export_path = pathlib.Path(r'C:\Users\mel-ama\TEASEROutput').joinpath(prj.name,"package.mo")
                                    print(model_export_path)
                                    main(
                                        aixlib_mo=r"C:\Users\mel-ama\sciebo2\Modelica\AixLib-development_1.0.2\AixLib\package.mo",
                                        teaser_mo=model_export_path,
                                        building_mo=prj.name+".B"+name+".B"+name,
                                        savepath=r"D:\00_temp",
                                        result_file_name=prj.name,
                                        n_cpu=1
                                    )
                                    if both_const:
                                        construction = "tabula_retrofit"
                                        prj.retrofit_all_buildings(
                                            year_of_retrofit=2015,
                                            type_of_retrofit="adv_retrofit",
                                            window_type='Alu- oder Stahlfenster, Isolierverglasung',
                                            material='EPS_perimeter_insulation_top_layer')

                                if both_heating:
                                    with_heating = not with_heating

                            if internal_gains_all:
                                internal_gains = internal_gains + 1

                        if both_layout:
                            residential_layout = residential_layout + 1

                    if both_ahu:
                        with_ahu = not with_ahu

                height_of_floors = height_of_floors + step_height_of_floors

            number_of_floors = number_of_floors + step_number_of_floors

        year_of_construction = year_of_construction + step_year_of_construction

    leased_area = leased_area + step_leased_area





