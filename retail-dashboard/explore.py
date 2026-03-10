import pandas as pd

# Load the dataset
df = pd.read_csv ("Sample - Superstore.csv", encoding="latin-1")


# --- BASIC EXPLORATION -- 

# See the first 5 rows
print("=== First 5 Rows ===")
print(df.head())
# See all columns
print("\n=== Columns ===")
print(df.columns.tolist())
# Check shape (rows, columns)
print("\n=== Shape ===")
print(df.shape)
# Check data types & nulls
print("\n=== Info ===")
print(df.info())
# Check stats on numeric columns
print("\n=== Summary Stats ===")
print(df.describe())
# Check for missing values
print("\n=== Missing Values ===")
print(df.isnull().sum())

