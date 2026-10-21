import pandas as pd
from sklearn.datasets import load_digits, load_wine
d = load_digits(as_frame=True)
df = d.data.copy(); df["target"] = d.target
df.to_csv("data/digits.csv", index=False)
w = load_wine(as_frame=True)
df = w.data.copy(); df["target"] = w.target
df["target_name"] = df["target"].map(dict(enumerate(w.target_names)))
df.to_csv("data/wine.csv", index=False)
print("saved")
