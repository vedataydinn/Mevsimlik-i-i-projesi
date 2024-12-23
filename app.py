from flask import Flask, jsonify, render_template
from elasticsearch import Elasticsearch
from pymongo import MongoClient

app = Flask(__name__)

# Elasticsearch bağlantısı
try:
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
    if not es.ping():
        print("Elasticsearch bağlantısı başarısız!")
except Exception as e:
    print(f"Elasticsearch bağlantısı sırasında bir hata oluştu: {e}")

# MongoDB bağlantısı
try:
    mongo_client = MongoClient('mongodb://admin:secret@localhost:27017/')
    mongo_db = mongo_client['mydatabase']  # Veritabanı adı
    print("MongoDB bağlantısı başarıyla yapıldı.")
except Exception as e:
    print(f"MongoDB bağlantısı sırasında bir hata oluştu: {e}")

# MongoDB koleksiyonları
workers_collection = mongo_db['workers']  # İşçiler koleksiyonu
jobs_collection = mongo_db['jobs']  # İş ilanları koleksiyonu
employers_collection = mongo_db['employers']  # İşverenler koleksiyonu

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ilan-ver')
def ilanVer():
    return render_template('ilan-ver.html')  # ilanVer.html sayfanız burada yüklenir






@app.route('/search/<index_name>/<query>')
def search(index_name, query):
    # Basit bir Elasticsearch araması
    response = es.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    "content": query
                }
            }
        }
    )
    return jsonify(response)

@app.route('/mongodb-test')
def mongodb_test():
    # MongoDB'de bir koleksiyon ve örnek bir belge oluşturma
    collection = mongo_db['test_collection']
    document = {"name": "Test User", "age": 30}
    collection.insert_one(document)
    return "MongoDB'ye veri eklendi!"

@app.route('/contact')  
def contact():
    return render_template('contact.html')


@app.route('/loginPage.html')  
def loginPage():
    return render_template('loginPage.html')

@app.route('/karakterBelirle.html')  
def karakterBlerile():
    return render_template('karakterBelirle.html')


@app.route('/Registerişveren.html')  
def Registerisveren():
    return render_template('Registerişveren.html')

@app.route('/Registerişci.html')  
def Registerisci():
    return render_template('Registerişci.html')


@app.route('/404')  
def not_found():
    return render_template('404.html')

# Veritabanına veri eklemek için bir örnek endpoint

@app.route('/add_worker')
def add_worker():
    # Örnek bir işçi verisi ekleyelim
    new_worker = {
        "id": 1,
        "ad": "Ahmet",
        "soyad": "Yılmaz",
        "telefon": "0533 123 4567",
        "eposta": "ahmet.yilmaz@gmail.com",
        "yas": 28,
        "cinsiyet": "Erkek",
        "deneyim": 3,
        "egitim": "Lise",
        "il": "Elazığ",
        "ilçe": "Merkez",
        "tercih_edilen_is_alanlari": "Kiraz Hasadı",
        "ucret_beklentisi": "15,000"
    }
    
    workers_collection.insert_one(new_worker)
    return "Yeni işçi başarıyla MongoDB'ye eklendi!"

@app.route('/add_job')
def add_job():
    # Örnek bir iş ilanı ekleyelim
    new_job = {
        "ilan_id": 1,
        "firma_adi": "XYZ Tarım",
        "is_pozisyonu": "Mevsimlik İşçi",
        "il": "Elazığ",
        "ilçe": "Sivrice",
        "köy": "Yedibağ",
        "çalışma_süresi": "3 Ay",
        "gerekli_egitim": "Lise",
        "tecrübe": "Yok",
        "yaş_sınırı": "18-35",
        "cinsiyet": "Erkek",
        "konaklama": "Var",
        "sigorta": "Var",
        "ücret": "3500 TL",
        "başvuru_durumu": "Açık"
    }

    jobs_collection.insert_one(new_job)
    return "Yeni iş ilanı başarıyla MongoDB'ye eklendi!"

@app.route('/add_employer')
def add_employer():
    # Örnek bir işveren verisi ekleyelim
    new_employer = {
        "id": 1,
        "ad": "Mehmet",
        "soyad": "Yıldız",
        "firma_adi": "Yıldız Tarım",
        "sektor": "Tarım ve Hayvancılık",
        "telefon": "0532 111 2233",
        "eposta": "mehmet.yildiz@tarim.com"
    }

    employers_collection.insert_one(new_employer)
    print("devam")
    return "Yeni işveren başarıyla MongoDB'ye eklendi!"

if __name__ == '__main__':
    app.run(debug=True)
 