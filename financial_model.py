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

def calculate_total_production_cost(electricity_cost, hydrogen_cost, co2_cost, water_cost, annualized_capex, profit_duration_days):
    return electricity_cost + hydrogen_cost + co2_cost + water_cost + annualized_capex/profit_duration_days

def calculate_profit(revenue, total_cost):
    return revenue - total_cost

def calculate_payback_period(capex, daily_profit):
    if daily_profit > 0:
        return capex / daily_profit
    else:
        return float('inf')  # Infinite if daily profit is zero or negative

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

    # Define CAPEX values and useful life
    capex_electrolysis = st.number_input("Enter the CAPEX for the electrolyser:", value=1000000)  # €1,000,000 for Electrolysis Equipment
    capex_hydrogen_storage = st.number_input("Enter the CAPEX for the hydrogen storage:", value=500000)  # €500,000 for Hydrogen Storage
    capex_co2_capture = st.number_input("Enter the CAPEX for the CO2 capturing infrastructure:", value=800000)  # €800,000 for CO2 Capture and Storage
    capex_esaf_production = st.number_input("Enter the CAPEX for the ATJ factory:", value=2000000)  # €2,000,000 for eSAF Production Facility
    useful_life_years = st.number_input("Enter the useful life of these assets:", value=10)  # Useful life of the assets in years

    # Calculate annualized CAPEX
    annualized_capex_electrolysis = capex_electrolysis / useful_life_years
    annualized_capex_hydrogen_storage = capex_hydrogen_storage / useful_life_years
    annualized_capex_co2_capture = capex_co2_capture / useful_life_years
    annualized_capex_esaf_production = capex_esaf_production / useful_life_years

    # Number of days it takes to generate the profit for all the scenarios
    profit_duration_days = st.number_input("Enter the number of days it takes to return a profit:", value=1) 

    # Initialize results list
    results = []

    # Define scenarios
    scenarios = [
        ("E", [electricity_price, electrolysis_ratio, 0, 0, fractionation_ratio, 0, 0, 0, 0, 0], "Supplying only electricity", 0),
        ("W", [0, 0, 0, 0, 0, 0, 0, water_price, water_quantity, 0], "Supplying only water for electrolysis", 0),
        ("EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Producing hydrogen through electrolysis", annualized_capex_electrolysis + annualized_capex_hydrogen_storage),
        ("CO2", [0, 0, 0, 0, 0, co2_price, co2_quantity, 0, 0, 0], "Acquiring and selling CO2", annualized_capex_co2_capture),
        ("C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Converting hydrogen and CO2 to eSAF", annualized_capex_esaf_production),
        ("E + W", [electricity_price, electrolysis_ratio, 0, 0, 0, 0, 0, water_price, water_quantity, 0], "Supplying electricity and water for electrolysis", 0),
        ("E + EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Supplying electricity and producing hydrogen", annualized_capex_electrolysis + annualized_capex_hydrogen_storage),
        ("E + CO2", [electricity_price, electrolysis_ratio, 0, 0, 0, co2_price, co2_quantity, 0, 0, 0], "Supplying electricity and acquiring CO2", annualized_capex_co2_capture),
        ("E + C", [electricity_price, electrolysis_ratio, 0, 0, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity and converting to eSAF", annualized_capex_esaf_production),
        ("W + EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Supplying water and producing hydrogen", annualized_capex_electrolysis + annualized_capex_hydrogen_storage),
        ("W + CO2", [electricity_price, electrolysis_ratio, 0, 0, 0, co2_price, co2_quantity, water_price, water_quantity, 0], "Supplying water and acquiring CO2", annualized_capex_co2_capture),
        ("W + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water and converting to eSAF", annualized_capex_esaf_production),
        ("EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, co2_price, co2_quantity, water_price, water_quantity, 0], "Producing hydrogen and acquiring CO2", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture),
        ("EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Producing hydrogen and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_esaf_production),
        ("CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Acquiring CO2 and converting to eSAF", annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("E + W + EP", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, 0, 0, water_price, water_quantity, 0], "Supplying electricity, water, and producing hydrogen", annualized_capex_electrolysis + annualized_capex_hydrogen_storage),
        ("E + W + CO2", [electricity_price, electrolysis_ratio, 0, 0, 0, co2_price, co2_quantity, water_price, water_quantity, 0], "Supplying electricity, water, and acquiring CO2", annualized_capex_co2_capture),
        ("E + W + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, and converting to eSAF", annualized_capex_esaf_production),
        ("E + EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, producing hydrogen, and acquiring CO2", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture),
        ("E + EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, producing hydrogen, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_esaf_production),
        ("E + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, acquiring CO2, and converting to eSAF", annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("W + EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, producing hydrogen, and acquiring CO2", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture),
        ("W + EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, producing hydrogen, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_esaf_production),
        ("W + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, acquiring CO2, and converting to eSAF", annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Producing hydrogen, acquiring CO2, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("H + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Handling hydrogen, acquiring CO2, and converting to eSAF", annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("E + W + EP + CO2", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, 0, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, producing hydrogen, and acquiring CO2", annualized_capex_electrolysis + annualized_capex_hydrogen_storage),
        ("E + W + EP + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, producing hydrogen, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_esaf_production),
        ("E + W + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, acquiring CO2, and converting to eSAF", annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("E + EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, producing hydrogen, acquiring CO2, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("W + EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying water, producing hydrogen, acquiring CO2, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture + annualized_capex_esaf_production),
        ("E + W + EP + CO2 + C", [electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price], "Supplying electricity, water, producing hydrogen, acquiring CO2, and converting to eSAF", annualized_capex_electrolysis + annualized_capex_hydrogen_storage + annualized_capex_co2_capture + annualized_capex_esaf_production)
    ]

    # Define the function to calculate costs and revenue based on the scenario
    def calculate_costs_and_revenue(scenario, values, annualized_capex):
        electricity_price, electrolysis_ratio, hydrogen_price, hydrogen_quantity, fractionation_ratio, co2_price, co2_quantity, water_price, water_quantity, esaf_selling_price = values[:10]

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

        # Check if we supply water
        if re.search(r'\bW\b', scenario) and not re.search(r'\bEP\b', scenario):
            revenue += calculate_water_cost(water_price, water_quantity)
            water_cost = 0
        elif not re.search(r'\bW\b', scenario) and re.search(r'\bEP\b', scenario):
            water_cost += calculate_water_cost(water_price, water_quantity)

        # Check if we supply electricity
        if re.search(r'\bE\b', scenario) and not re.search(r'\b(EP)\b', scenario):
            revenue += electricity_price * electrolysis_ratio  # Revenue from selling electricity
            electricity_cost = 0  # No production cost if just selling electricity
        
        if re.search(r'\bE\b', scenario) and not re.search(r'\b(C)\b', scenario):
            revenue += electricity_price * electrolysis_ratio  # Revenue from selling electricity
            electricity_cost += electricity_price * fractionation_ratio

        if re.search(r'\bEP\b', scenario) and not re.search(r'\bC\b', scenario):
            revenue += hydrogen_price * hydrogen_quantity  # Revenue from selling hydrogen

        if re.search(r'\bCO2\b', scenario) and not re.search(r'\bC\b', scenario):
            revenue += co2_price * co2_quantity  # Revenue from selling CO2
            co2_cost = 0

        # Check if we convert to eSAF
        if re.search(r'\bC\b', scenario):
            electricity_cost += calculate_electricity_cost(electricity_price, fractionation_ratio)
            co2_cost += calculate_co2_cost(co2_price, co2_quantity)
            revenue += esaf_selling_price
            if not re.search(r'\bEP\b', scenario):
                hydrogen_cost += calculate_hydrogen_cost(hydrogen_price, hydrogen_quantity)  # Hydrogen cost if not produced internally

        total_production_cost = calculate_total_production_cost(electricity_cost, hydrogen_cost, co2_cost, water_cost, annualized_capex, profit_duration_days)

        profit = calculate_profit(revenue, total_production_cost)

        return {
            "Scenario": scenario,
            "Description": description,
            "Electricity Cost (€)": electricity_cost,
            "Hydrogen Cost (€)": hydrogen_cost,
            "CO2 Cost (€)": co2_cost,
            "Water Cost (€)": water_cost,
            "Annualized CAPEX (€)": annualized_capex,
            "Total Production Cost (€)": total_production_cost,
            "Revenue (€)": revenue,
            "Profit (€)": profit
        }

    # Loop through scenarios and calculate costs and profits
    for scenario, values, description, annualized_capex in scenarios:
        result = calculate_costs_and_revenue(scenario, values, annualized_capex)
        payback_period_days = calculate_payback_period(annualized_capex * useful_life_years, result["Profit (€)"])
        result["Payback Period (days)"] = payback_period_days
        results.append(result)

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

    # Display payback period information
    st.write("Payback Period (days) per Scenario")
    st.write(results_df[['Scenario', 'Payback Period (days)']])

if __name__ == "__main__":
    main()
