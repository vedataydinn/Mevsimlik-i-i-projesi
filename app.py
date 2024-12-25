from flask import Flask, jsonify, render_template, request
from elasticsearch import Elasticsearch
from pymongo import MongoClient
import joblib
from bson import ObjectId



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







# ObjectId'yi JSON uyumlu hale getirme
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj




@app.route('/')
def index():
    try:
        jobs = jobs_collection.find()
        jobs_list = list(jobs)
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        jobs_list = []

    settings = {
        "isShowFilterMode": False
    }
    return render_template('index.html', jobs=jobs_list, settings=settings)

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


@app.route('/ilanVer')  
def ilanVer():
    return render_template('ilan-Ver.html')


@app.route('/loginPage.html')  
def loginPage():
    return render_template('loginPage.html')

@app.route('/karakterBelirle.html')  
def karakterBelirle():
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

# İşçi Kaydı
@app.route('/Registerişci.html', methods=['GET', 'POST'])
def register_worker():
    if request.method == 'POST':
        # Formdan gelen verileri alıyoruz
        worker = {
            "Ad": request.form.get("fname"),
            "Soyad": request.form.get("lname"),
            "Yaş": int(request.form.get("yas")),
            "Telefon Numarası": request.form.get("phone"),
            "Eğitim": request.form.get("egitim"),
            "Deneyim (Yıl)": int(request.form.get("deneyim")),
            "Şehir": request.form.get("sehir"),
            "İlçe": request.form.get("ilce"),
            "Tercih Edilen İş Alanları": request.form.get("isAlanlari"),
            "Ücret Beklentisi": int(request.form.get("ucretBeklentisi")),
            "E-Posta": request.form.get("email"),
            "Şifre": request.form.get("password")
        }
        # MongoDB'ye kaydediyoruz
        workers_collection.insert_one(worker)
        return "İşçi başarıyla kayıt edildi!"
    return render_template('Registerişci.html')
# İşveren Kaydı
@app.route('/Registerişveren.html', methods=['GET', 'POST'])
def register_employer():
    if request.method == 'POST':
        # Formdan gelen verileri alıyoruz
        employer = {
            "Ad": request.form.get("fname"),
            "Soyad": request.form.get("lname"),
            "Firma Adı": request.form.get("firmaAdi"),
            "Telefon Numarası": request.form.get("phone"),
            "Şehir": request.form.get("sehir"),
            "İlçe": request.form.get("ilce"),
            "E-Posta": request.form.get("email"),
            "Şifre": request.form.get("password")
        }
        # MongoDB'ye kaydediyoruz
        employers_collection.insert_one(employer)
        return "İşveren başarıyla kayıt edildi!"
    return render_template('Registerişveren.html')











if __name__ == '__main__':
    app.run(debug=True)


