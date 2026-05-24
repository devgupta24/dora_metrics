import pandas as pd

def get_df():
    return pd.DataFrame([["Alice",48,"Engineer"],["Bob",28,"Designer"]],
                        columns=["Name","Age","Role"])


if __name__ == "__main__":
    df = get_df()
    print(df.to_string(index=False))