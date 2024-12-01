import pandas as pd

length = 43
weight = 5
age = 0
dataset = pd.read_excel('dataset_baby/PB laki laki 0-2 thn.xlsx')
def calculate_z_score():
    row = dataset[dataset['Umur'] == age]
    if row.empty:
        raise ValueError(f"Data tidak ditemukan untuk umur {age} bulan.")
    median = row['Median'].values[0]
    minus_1_sd = row['-1 SD'].values[0]
    plus_1_sd = row['+1 SD'].values[0]
    if length < median:
        z_score = (length - median) / (median - minus_1_sd)
    else:
        z_score = (length - median) / (plus_1_sd - median)
    return z_score

print(calculate_z_score())