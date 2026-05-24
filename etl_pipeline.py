import pandas as pd
df = pd.DataFrame([["Alice",48,"Engineer"],["Bob",28,"Designer"],["Bob1",29,"Doctor"]],
                  columns=["Name","Age","Role"])
print("DORA Metrics Dashboard")
print(df.to_string(index=False))
