import pandas as pd

# Excel dosyasını oku
df = pd.read_excel('YastıkSon.xlsx')

print("Excel dosyasındaki sütun isimleri:")
print(df.columns.tolist())

print("\nİlk 3 satır:")
print(df.head(3)) 