import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import re


def calculate_electricity_cost(electricity_price, energy_needed):
    return electricity_price * energy_needed

def calculate_hydrogen_cost(hydrogen_price, hydrogen_quantity):
    return hydrogen_price * hydrogen_quantity

def calculate_co2_cost(co2_price, co2_quantity):
    return co2_price * co2_quantity

def calculate_water_cost(water_price, water_quantity):
    return water_price * water_quantity

def calculate_total_production_cost(electricity_cost, hydrogen_cost, co2_cost, water_cost):
    return electricity_cost + hydrogen_cost + co2_cost + water_cost

def calculate_profit(revenue, total_cost):
    return revenue - total_cost

def main():
    # Get user inputs
    st.title("Financial Model for eSAF Production")

    # Get user inputs
    electricity_price = st.number_input("Enter the price of electricity per MWh:", value=50.0)
    electrolysis_ratio = st.number_input("Enter the energy required for electrolysis in MWh:", value=27.5)
    hydrogen_price = st.number_input("Enter the price of hydrogen per kg:", value=6.0)
    hydrogen_quantity = st.number_input("Enter the quantity of hydrogen produced in kg:", value=250.0)
    fractionation_ratio = st.number_input("Enter the energy required for the fractionation process in MWh:", value=12.5)
    co2_price = st.number_input("Enter the price of CO2 per ton:", value=500.0)
    co2_quantity = st.number_input("Enter the quantity of CO2 required in tons:", value=1.8)
    water_price = st.number_input("Enter the price of water per cubic meter:", value=0.0)
    water_quantity = st.number_input("Enter the quantity of water required in cubic meters:", value=7.0)
    esaf_selling_price = st.number_input("Enter the selling price of eSAF per cubic meter:", value=2750.0)


    # Initialize results list
    results = []
 
     # Define scenarios
    scenarios = [
                 
        ("E", [electricity_price, electrolysis_ratio, 0, 0, fractionation_ratio, 0, 0, 0, 0, 0], "Supplying only electricity"),
        ("W", [0, 0, 0, 0, 0, 0, 0, water_price, water_quantity, 0], "Supplying only water for electrolysis"),
        ("EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Producing hydrogen through electrolysis"),
        ("H", [0, 0, hydrogen_price, hydrogen_quantity, 0, 0, 0, 0, 0, 0], "Handling and selling hydrogen"),
        ("CO2", [0, 0, 0, 0, 0, co2_price, co2_quantity, 0, 0, 0], "Acquiring and selling CO2"),
        ("C", [electricity_price, electrolysis_ratio, 0, 0, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Converting hydrogen and CO2 to eSAF"),
        ("E + W", [electricity_price, 0, 0, 0, 0, 0, 0, water_price, water_quantity, 0], "Supplying electricity and water for electrolysis"),
        ("E + EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Supplying electricity and producing hydrogen"),
        ("E + CO2", [electricity_price, 0, 0, 0, 0, co2_price, co2_quantity, 0, 0, 0], "Supplying electricity and acquiring CO2"),
        ("E + C", [electricity_price, electrolysis_ratio, 0, 0, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity and converting to eSAF"),
        ("W + EP", [0, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Supplying water and producing hydrogen"),
        ("W + CO2", [0, electrolysis_ratio, 0, 0, 0, co2_price, co2_quantity, water_price, water_quantity, 0], "Supplying water and acquiring CO2"),
        ("W + C", [0, electrolysis_ratio, 0, 0, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water and converting to eSAF"),
        ("EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, co2_price, co2_quantity, water_price, water_quantity, 0], "Producing hydrogen and acquiring CO2"),
        ("EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Producing hydrogen and converting to eSAF"),
        ("CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Acquiring CO2 and converting to eSAF"),
        ("E + W + EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Supplying electricity, water, and producing hydrogen"),
        ("E + W + CO2", [electricity_price, electrolysis_ratio, 0, 0, 0, co2_price, co2_quantity, water_price, water_quantity, 0], "Supplying electricity, water, and acquiring CO2"),
        ("E + W + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, and converting to eSAF"),
        ("E + EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, producing hydrogen, and acquiring CO2"),
        ("E + EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, producing hydrogen, and converting to eSAF"),
        ("E + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, acquiring CO2, and converting to eSAF"),
        ("W + EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, producing hydrogen, and acquiring CO2"),
        ("W + EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, producing hydrogen, and converting to eSAF"),
        ("W + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, acquiring CO2, and converting to eSAF"),
        ("EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Producing hydrogen, acquiring CO2, and converting to eSAF"),
        ("H + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Handling hydrogen, acquiring CO2, and converting to eSAF"),
        ("E + W + EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, producing hydrogen, and acquiring CO2"),
        ("E + W + EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, producing hydrogen, and converting to eSAF"),
        ("E + W + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, acquiring CO2, and converting to eSAF"),
        ("E + EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, producing hydrogen, acquiring CO2, and converting to eSAF"),
        ("W + EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, producing hydrogen, acquiring CO2, and converting to eSAF"),
        ("E + W + EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, producing hydrogen, acquiring CO2, and converting to eSAF"),
    ]

    # Define the function to calculate costs and revenue based on the scenario
    def calculate_costs_and_revenue(scenario, values):
        electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price = values[:10]
        energy_needed = electrolysis_ratio + fractionation_ratio

        # Calculate costs
        electricity_cost = 0
        hydrogen_cost = 0
        co2_cost = 0
        water_cost = 0
        total_production_cost = 0
        revenue = 0

        # Check if we produce hydrogen through electrolysis
        if re.search(r'\bEP\b', scenario):
            electricity_cost += calculate_electricity_cost(electricity_price, electrolysis_ratio)
            water_cost += calculate_water_cost(water_price, water_quantity)
            hydrogen_cost = 0  # Hydrogen cost is 0 when we are producing it internally

        # Check if we convert to eSAF
        if re.search(r'\bC\b', scenario):
            electricity_cost += calculate_electricity_cost(electricity_price, fractionation_ratio)
            co2_cost += calculate_co2_cost(co2_price, co2_quantity)
            if not re.search(r'\bEP\b', scenario):
                hydrogen_cost += calculate_hydrogen_cost(hydrogen_price, hydrogen_quantity)  # Hydrogen cost if not produced internally


        # Check if we acquire and sell CO2
        if re.search(r'\bCO2\b', scenario) and not re.search(r'\bC\b', scenario):
            co2_cost += calculate_co2_cost(co2_price, co2_quantity)

        # Check if we supply water
        if re.search(r'\bW\b', scenario) and not re.search(r'\bEP\b', scenario):
            water_cost += calculate_water_cost(water_price, water_quantity)

        # Check if we supply electricity
        if re.search(r'\bE\b', scenario) and not re.search(r'\b(EP|C)\b', scenario):
            revenue += electricity_price * electrolysis_ratio  # Revenue from selling electricity
            electricity_cost = 0  # No production cost if just selling electricity

        total_production_cost = calculate_total_production_cost(electricity_cost, hydrogen_cost, co2_cost, water_cost)

        # Calculate revenue based on the scenario
        if re.search(r'\bC\b', scenario):
            revenue += esaf_selling_price  # Revenue from selling eSAF

        if re.search(r'\bEP\b', scenario) and not re.search(r'\bH\b', scenario):
            revenue += hydrogen_price * hydrogen_quantity  # Revenue from selling hydrogen

        if re.search(r'\bH\b', scenario) and not re.search(r'\bEP\b', scenario):
            revenue += hydrogen_price * hydrogen_quantity  # Revenue from handling and selling hydrogen

        if re.search(r'\bCO2\b', scenario) and not re.search(r'\bC\b', scenario):
            revenue += co2_price * co2_quantity  # Revenue from selling CO2

        profit = calculate_profit(revenue, total_production_cost)

        return {
            "Scenario": scenario,
            "Description": description,
            "Electricity Cost (€)": electricity_cost,
            "Hydrogen Cost (€)": hydrogen_cost,
            "CO2 Cost (€)": co2_cost,
            "Water Cost (€)": water_cost,
            "Total Production Cost (€)": total_production_cost,
            "Revenue (€)": revenue,
            "Profit (€)": profit
        }

    # Loop through scenarios and calculate costs and profits
    for scenario, values, description in scenarios:
        result = calculate_costs_and_revenue(scenario, values)
        results.append(result)

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Display results
    print(results_df)
        # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Display results
    st.write(results_df)

    # Plot results
    st.write("Profit per Scenario")
    fig, ax = plt.subplots(figsize=(15, 8))
    results_df.plot(x='Scenario', y='Profit (€)', kind='bar', ax=ax, legend=False)
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Profit (€)")
    ax.set_title("Profit per Scenario")
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig)
if __name__ == "__main__":
    main()