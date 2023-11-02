import os
import glob
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
charges_file_paths = glob.glob(os.path.join(parent_dir, 'data', 'EV_charges', '*.xlsx'))
emissions_file_path = glob.glob(os.path.join(parent_dir, 'data','CO2_data', '*.csv'))
files_not_processed = []
print(f"\nScript directory: {script_dir}")
print("\n_________________________________________________________________\n")
print("List of file paths for charges:\n")
for file_path in charges_file_paths:
    print(file_path)
print("\n_________________________________________________________________\n")
print("List of file paths for CO2 emissions:\n")
for file_path in emissions_file_path:
    print(file_path)

def charges_file_opener(file_paths):
    month_dfs = []
    count = 0
    file_not_processed = []
    for file in file_paths:
        print(f"\nProcessing: {file}")
        try:
            raw_df = (pd.read_excel(file, engine='openpyxl', skiprows=6, header=0))
            disclaimer_rows = raw_df[raw_df.map(lambda x: str(x).startswith('*') or str(x).startswith('mobile20chsDisclaimer')).any(axis=1)]
            if not disclaimer_rows.empty:
                limit_index = disclaimer_rows.index[0]
                df = raw_df.iloc[:limit_index-3].dropna(subset=['Conectado'])
            else:
                print(f"\n!No disclaimer cell(*) found in file: {file}. Aggregating whole data.\n")
                df = raw_df.dropna(subset=['Conectado'])
            count += 1
            print(f"\nShape of the DataFrame (no {count}): {df.shape}")
            print(f"\nNumber of charges for the loaded DataFrame: {df.shape[0]}\n")
            month_dfs.append(df)
        except Exception as e:
            print(f"!!!Error processing file: {file}. Error: {e}\n")
            files_not_processed.append(file)
            continue
    if len(files_not_processed) > 0:
        print(f"File(s) not processed: {files_not_processed}")
    complete_df = pd.concat(month_dfs)
    return complete_df

def emissions_file_opener(file_path):
    emissions_dfs = []
    count = 0
    files_not_processed = []
    for file in file_path:
        print(f"\nProcessing: {file}")
        try:
            raw_df = pd.read_csv(file)
            count += 1
            print(f"\nShape of the DataFrame (no {count}): {raw_df.shape}")
            print(f"\nNumber of charges for the loaded DataFrame: {raw_df.shape[0]}\n")
            emissions_dfs.append(raw_df)
        except Exception as e:
            print(f"!!!Error processing file: {file}. Error: {e}\n")
            files_not_processed.append(file)
            continue
    if len(files_not_processed) > 0:
        print(f"File(s) not processed: {files_not_processed}")
    complete_df = pd.concat(emissions_dfs)
    return complete_df

def charges_df_cleaning(df, anonym=True):
    en_columns = ['charge_start_time',
                  'km_mileage',
                  'initial_soc',
                  'charge_end_time',
                  'final_soc',
                  'local',
                  'address',
                  'charge_costs',
                  'kwh',
                  'electricity_price1',
                  'electricity_price2',
                  'charge_duration_min',
                  'ac_at_startup']
    if len(df.columns) == len(en_columns):
        df.columns = en_columns
    else:
        print("Number of columns doesn't match, please review the imported files.")
    df['charge_start_time'] = pd.to_datetime(df['charge_start_time'], dayfirst=True)
    df['km_mileage'] = df['km_mileage'].str.findall('(\d+)').str.join('').astype(int)
    df['charge_end_time'] = pd.to_datetime(df['charge_end_time'], dayfirst=True)
    df = df.drop(['local'], axis=1)
    df['kwh'] = df['kwh'].str.extract('(\d+)')[0].astype(float)
    if not df['electricity_price1'].str.contains(r'\d').any():
        df = df.drop(['charge_costs', 'electricity_price1'], axis=1)
    if not df['electricity_price2'].str.contains(r'\d').any():
        df = df.drop('electricity_price2', axis=1)
    df['hours'] = [int(x.split('h')[0]) if 'h' in str(x) else 0 for x in df['charge_duration_min']]
    df['minutes'] = [int(x.split('min')[0].split()[-1]) if 'min' in str(x) else 0 for x in df['charge_duration_min']]
    df['charge_duration_min'] = df['hours'] * 60 + df['minutes']
    df.drop(['hours', 'minutes'], axis=1, inplace=True)
    if anonym:
        df.drop(['address'], axis=1, inplace=True)
    return df

def co2_df_cleaning(df):
    df['Datetime (UTC)'] = pd.to_datetime(df['Datetime (UTC)'])
    return df
        
def display_df_info(df):
    # Display basic information about the DataFrame
    print("\nNEW DATA FRAME INFORMATION_________________________________________________________________")
    print(f"\nShape of the DataFrame: {df.shape}")
    print(f"\nNumber of rows: {df.shape[0]}")
    print(f"\nNumber of columns: {df.shape[1]}")
    print(f"\nData frame description : \n{df.describe(include ='all')}")
    print("\n_________________________________________________________________")

    # List column names for reference and columns info
    print(f"\nColumn names:\n{df.columns.tolist()}")
    print(f"\nColumns types: \n{df.info()}")

    # Display the first few and last few rows of the DataFrame to visually inspect some data
    print("\nFirst 5 rows of the DataFrame:")
    print(df.head(5))

    print("\nLast 5 rows of the DataFrame:")
    print(df.tail(5))

def calculate_direct_emissions(charge_row, co2_df):
    start_time = charge_row['charge_start_time']
    end_time = charge_row['charge_end_time']
    charge_rate = charge_row['charge_rate']
    
    mask = (co2_df['Datetime (UTC)'] >= start_time) & (co2_df['Datetime (UTC)'] <= end_time)
    relevant_co2_data = co2_df[mask]
    
    total_emissions = 0.0
    
    for i, row in relevant_co2_data.iterrows():
        co2_time_start = row['Datetime (UTC)']
        co2_time_end = co2_time_start + pd.Timedelta(hours=1)
        overlap_start = max(start_time, co2_time_start)
        overlap_end = min(end_time, co2_time_end)
        overlap_minutes = (overlap_end - overlap_start).seconds / 60.0
        emissions = charge_rate * (overlap_minutes / 60.0) * row['Carbon Intensity gCO₂eq/kWh (direct)']
        
        total_emissions += emissions
    
    return total_emissions

def calculate_lca_emissions(charge_row, co2_df):
    start_time = charge_row['charge_start_time']
    end_time = charge_row['charge_end_time']
    charge_rate = charge_row['charge_rate']
    
    mask = (co2_df['Datetime (UTC)'] >= start_time) & (co2_df['Datetime (UTC)'] <= end_time)
    relevant_co2_data = co2_df[mask]
    
    total_emissions = 0.0
    
    for i, row in relevant_co2_data.iterrows():
        co2_time_start = row['Datetime (UTC)']
        co2_time_end = co2_time_start + pd.Timedelta(hours=1)
        overlap_start = max(start_time, co2_time_start)
        overlap_end = min(end_time, co2_time_end)
        overlap_minutes = (overlap_end - overlap_start).seconds / 60.0
        emissions = charge_rate * (overlap_minutes / 60.0) * row['Carbon Intensity gCO₂eq/kWh (LCA)']
        
        total_emissions += emissions
    
    return total_emissions

if __name__ == "__main__":
    print("CO2 Datframe information :\n")
    co2_df = emissions_file_opener(emissions_file_path)
    co2_df = co2_df_cleaning(co2_df)
    display_df_info(co2_df)
    print("Charges Datframe information :\n")
    charges_df = charges_file_opener(charges_file_paths)
    charges_df = charges_df_cleaning(charges_df)
    charges_df['charge_rate'] = charges_df['kwh'] / (charges_df['charge_duration_min'] / 60)
    charges_df['co2_direct_emissions'] = charges_df.apply(lambda row: calculate_direct_emissions(row, co2_df), axis=1)
    charges_df['co2_lca_emissions'] = charges_df.apply(lambda row: calculate_lca_emissions(row, co2_df), axis=1)
    display_df_info(charges_df)