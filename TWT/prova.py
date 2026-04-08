import pandas as pd
df = pd.read_csv("sweep_results/sweep_completo.csv")
print(df.to_string())