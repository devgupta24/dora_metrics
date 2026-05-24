import re
import pandas as pd

def validate_df(df, allowed_roles=None, name_pattern=r"^[A-Za-z ]+$", min_age=0, max_age=120):
    report = {}
    # required columns
    required = ["Name", "Age", "Role"]
    report["missing_columns"] = [c for c in required if c not in df.columns]
    if report["missing_columns"]:
        return report

    # missing values
    report["missing_values"] = df[required].isna().sum().to_dict()

    # duplicates
    report["duplicate_rows"] = int(df.duplicated().sum())
    report["duplicate_names"] = int(df["Name"].duplicated().sum())

    # Age numeric + range
    age_conv = pd.to_numeric(df["Age"], errors="coerce")
    report["age_non_numeric_count"] = int(age_conv.isna().sum() - df["Age"].isna().sum())
    report["age_out_of_range"] = int(((age_conv < min_age) | (age_conv > max_age)).sum())

    # Role allowed values
    if allowed_roles is None:
        allowed_roles = {"Engineer", "Designer"}
    roles = set(df["Role"].dropna().astype(str).unique())
    report["unknown_roles"] = sorted(list(roles - set(allowed_roles)))

    # Name pattern
    bad_names = df["Name"].astype(str).apply(lambda s: not bool(re.match(name_pattern, s)))
    report["invalid_name_count"] = int(bad_names.sum())

    # Basic shape checks
    report["row_count"] = int(len(df))
    report["column_count"] = int(len(df.columns))

    return report

# Example usage with your df
if __name__ == "__main__":
    df = pd.DataFrame([["Alice",48,"Engineer"],["Bob",28,"Designer"]],
                      columns=["Name","Age","Role"])
    print(validate_df(df))
    # missing values per column
    print(df.isna().sum())

    # find duplicate rows
    print(df[df.duplicated()])

    # invalid ages (non-numeric or out of range)
    ages = pd.to_numeric(df["Age"], errors="coerce")
    print(df[ages.isna() | (ages < 0) | (ages > 120)])

    # roles outside allowed set
    allowed = {"Engineer","Designer"}
    print(df[~df["Role"].isin(allowed)])

    # names with non-alpha chars
    print(df[~df["Name"].astype(str).str.match(r"^[A-Za-z ]+$")])