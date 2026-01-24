import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data= pd.read_csv("clients.csv")
print(data.head())
print(data.tail())
print(data.info())
email= data['email']
print(email)
print(data.loc[0:10, :])
print(data.iloc[0:10, :])