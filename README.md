# Bimmer Electric Vehicle Charges Inspector

## Overview

This script aims to read the data regarding the charges of BMW/Mini electric vehicles and additionally calculate an estimation of the amount of CO2 (equivalent) emitted for each charge in order to allow an easy analysis of this data. by using Pandas dataframes.

## Dependencies

- Python 3.x
- Pandas
- NumPy
- openpyxl

## Data Sources

### Charging Data

- Download the `.xlsx` files available in the "my BMW" app.

### Carbon Intensity Data

- Download the `.csv` files from [Electricity Maps](https://www.electricitymaps.com/data-portal).
- **Direct Download**: [Free Data](https://www.electricitymaps.com/data-portal#download-free-data)
- **Format**: `.csv`
- **License**: Open Database License (ODbL)

## Directory Structure

Place the `.xlsx` files related to the charges in a folder named `EV_charges` and the `.csv` files related to the carbon intensity in a folder named `CO2_data`. Both of these folders should be in the same directory as the script.

```

|-- src
|   |-- bimmer_ev_charges_inspector.py
|-- data
|   |-- EV_charges
|   |   |-- charges_excel_file.xlsx
|   |   |-- ...
|   |-- CO2_data
|   |   |-- co2_intensity_files.csv
|   |   |-- ...
|-- README.md

```

## Functions

Here's a breakdown of the primary functions within the script:

### `charges_file_opener(file_paths)`

Opens and aggregates charge data from multiple `.xlsx` files.

### `emissions_file_opener(file_path)`

Opens and aggregates CO2 emissions data from multiple `.csv` files.

### `charges_df_cleaning(df, anonym=True)`

Cleans the charges DataFrame and optionally anonymizes it by removing the charges location.

### `co2_df_cleaning(df)`

Cleans the CO2 DataFrame by changing the datatipe of the date into ``datetime``.

### `display_df_info(df)`

Displays basic info about a DataFrame.

### `calculate_direct_emissions(charge_row, co2_df)`

Calculates the direct CO2 emissions for a given charge, in 'grams of CO2 equivalent'.

### `calculate_lca_emissions(charge_row, co2_df)`

Calculates the life cycle CO2 emissions for a given charge, in 'grams of CO2 equivalent'.

## Usage

After placing the required `.xlsx` and `.csv` files in their respective directories, run the script. It will process the files and output DataFrames containing charges and CO2 emissions data. The script will also calculate direct and life cycle CO2 emissions for each charge.

## Limitations

The CO2 emissions estimations in this project have some limitations to be aware of:

#### Charge Curve

The script assumes a uniform charge rate throughout the charging session. However, electric vehicles typically charge faster at the beginning of the charge cycle, introducing a slight margin of error in the CO2 emissions estimation.

#### Grid Losses

The kWh values used for the charges are the amounts of electricity that directly reach the vehicle. These figures do not account for potential energy losses that occur in the electrical grid, which could affect the overall CO2 emissions.

## Troubleshooting

- Make sure the `.xlsx` and `.csv` files are placed in the correct directories (`EV_charges` and `CO2_data`, respectively).
- Ensure you have installed all the required Python packages.

## Contributing

Feel free to fork this project, make changes, and submit pull requests.
