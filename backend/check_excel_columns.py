import pandas as pd

# Excel dosyasını oku
df = pd.read_excel('yastiklar.xlsx', header=2, sheet_name='MATRİS GÜNCEL')

print("Sütun isimleri ve sırası:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print(f"\nToplam {len(df.columns)} sütun var.")

# Uyku pozisyonu sütununu bul (sütun 3)
uyku_pozisyonu_col = df.columns[3]
print(f"\nUyku pozisyonu sütunu: {uyku_pozisyonu_col}")

print(f"\nUyku pozisyonu sütununun ilk 10 değeri:")
for i in range(min(10, len(df))):
    value = df.iloc[i, 3]
    print(f"Satır {i}: {value}")
    if isinstance(value, str) and len(value) > 100:
        print(f"  (Uzun string - ilk 100 karakter: {value[:100]}...)")

print(f"\nUyku pozisyonu sütununun tüm benzersiz değerleri:")
unique_values = df.iloc[:, 3].unique()
for i, value in enumerate(unique_values):
    print(f"{i}: {value}")
    if isinstance(value, str) and len(value) > 100:
        print(f"  (Uzun string - ilk 100 karakter: {value[:100]}...)")

print(f"\nUyku pozisyonu sütununun veri tipi:")
print(f"İlk değerin tipi: {type(df.iloc[0, 3])}")
print(f"İkinci değerin tipi: {type(df.iloc[1, 3])}")

# Eğer liste formatında ise, ilk birkaç değeri parse etmeye çalış
print(f"\nİlk satırın uyku pozisyonu değerini eval ile parse etmeye çalışıyoruz:")
try:
    first_value = df.iloc[1, 3]  # İlk veri satırı
    if isinstance(first_value, str) and first_value.startswith('['):
        parsed = eval(first_value)
        print(f"Parse edilen değer: {parsed}")
        print(f"Tip: {type(parsed)}")
        if isinstance(parsed, list):
            print(f"Liste uzunluğu: {len(parsed)}")
            print(f"İlk 5 eleman: {parsed[:5]}")
except Exception as e:
    print(f"Parse hatası: {e}")

print(f"\nİlk 3 satır:")
print(df.head(3))

print(f"\nİlk satırın tüm değerleri:")
print(df.iloc[0])

print(f"\nSütun 0'ın ilk 5 değeri:")
print(df.iloc[:5, 0])

print(f"\nSütun 8'ın ilk 5 değeri (sertlik olması gereken):")
print(df.iloc[:5, 8])

print(f"\nSütun 9'ın ilk 5 değeri (görsel):")
print(df.iloc[:5, 9])

print(f"\nSütun 10'ın ilk 5 değeri (link):")
print(df.iloc[:5, 10])

print(f"\nTüm sütunların ilk satırı:")
for i, col in enumerate(df.columns):
    print(f"Sütun {i} ({col}): {df.iloc[0, i]}")

print(f"\nSütun 7'nin ilk 5 değeri (doğal malzeme):")
print(df.iloc[:5, 7]) 