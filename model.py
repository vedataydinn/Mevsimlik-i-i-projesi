# İşçi ve İlan Eşleşmesi için Makine Öğrenimi Modeli

## Adım 1: Gerekli Kütüphaneleri İçe Aktarma
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib  # Modeli kaydetmek için


## Adım 2: Veri Yükleme
df = pd.read_csv("C:\\Users\\Vedat\\Desktop\\mevsim\\mevsimlik_yapayzekaveriseti3.csv")

df.head()  # Verinin ilk 5 satırını görüntüleyelim


## Adım 3: Gerekli Sütunların Seçilmesi
features = [
    "Isci_Yas", "Isci_Egitim", "Isci_Tecrube", "Isci_Beklenen_Ucret", 
    "Ilan_Is_Alani", "Ilan_Sehir", "Ilan_Ilce", "Ilan_Egitim_Gereksinimi", 
    "Ilan_Tecrube_Sarti", "Ilan_Ucret", "Ilan_Yas_Siniri", "Ilan_Cinsiyet", 
    "Ilan_Konaklama", "Ilan_Sigorta"
]
target = "Uygunluk"

df = df[features + [target]]  # Sadece gerekli sütunları tut


# Adım 4: Kategorik Değişkenlerin Dönüştürülmesi
label_encoders = {}
for column in ["Isci_Egitim", "Ilan_Is_Alani", "Ilan_Sehir", "Ilan_Ilce", "Ilan_Egitim_Gereksinimi", "Ilan_Cinsiyet", "Ilan_Konaklama", "Ilan_Sigorta"]:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    label_encoders[column] = le  # Encoderları kaydet

# Yaş aralığını ortalama yaş olarak dönüştür
def convert_age_range(age_range):
    if isinstance(age_range, str) and '-' in age_range:
        start, end = age_range.split('-')
        return (int(start) + int(end)) / 2  # Ortalamayı al
    return float(age_range)  # Eğer tek bir yaş değeri varsa, doğrudan sayıya dönüştür

df['Ilan_Yas_Siniri'] = df['Ilan_Yas_Siniri'].apply(convert_age_range)

df.head()  # Dönüşüm sonrası veriyi kontrol edelim



## Adım 5: Özellikler ve Hedef Değişken Ayrımı
X = df[features]
y = df[target]

# Veriyi normalize etme
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

## Adım 6: Veriyi Eğitim ve Test Olarak Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


## Adım 7: Model Oluşturma ve Eğitme
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

## Adım 8: Modeli Değerlendirme
score = model.score(X_test, y_test)
print(f"Model Test Skoru: {score:.2f}")

## Adım 9: Modeli ve Dönüşüm Araçlarını Kaydetme
joblib.dump(model, "isci_ilan_modeli.pkl")
joblib.dump(scaler, "isci_ilan_scaler.pkl")
joblib.dump(label_encoders, "isci_ilan_label_encoders.pkl")

print("Model ve araçlar başarıyla kaydedildi.")