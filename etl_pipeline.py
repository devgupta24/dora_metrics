import pandas as pd
df = pd.DataFrame([["Alice",24,"Engineer"],["Bob",30,"Designer"]],
                  columns=["Name","Age","Role"])
print(df.to_string(index=False))