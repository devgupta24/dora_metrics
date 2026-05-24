import pandas as pd
df = pd.DataFrame([["Alice",48,"Engineer"],["Bob",28,"Designer"]],
                  columns=["Name","Age","Role"])
                  
print(df.to_string(index=False))