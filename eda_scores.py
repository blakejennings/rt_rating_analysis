import pandas as pd

# Read csv files into pandas dataframes
amazon_prime = pd.read_csv("./scores/amazon_prime.csv")
amazon = pd.read_csv("./scores/amazon.csv")
itunes = pd.read_csv("./scores/itunes.csv")
netflix = pd.read_csv("./scores/netflix_iw.csv")
vudu = pd.read_csv("./scores/vudu.csv")

print(amazon_prime)
print(amazon)
print(itunes)
print(netflix)
print(vudu)