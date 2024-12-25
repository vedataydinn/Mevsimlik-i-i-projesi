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
        # MongoDB'den iş ilanlarını alıyoruz
        jobs = jobs_collection.find()  # Koleksiyonun tamamını al
        jobs_list = list(jobs)  # MongoDB cursor'ını listeye dönüştür
        # ObjectId'yi string'e çevir
        jobs_list = [serialize_objectid(job) for job in jobs_list]
        settings = {"isShowFilterMode": True}  # Örnek settings değişkeni
        print(jobs_list)  # jobs_list burada tanımlandı ve kullanılabilir
    except Exception as e:
        print("Veritabanı hatası:", e)
        jobs_list = []  # Hata durumunda boş bir liste döndür
        settings = {"isShowFilterMode": False}  # Hata durumunda varsayılan bir ayar

    return render_template('index.html', jobs=jobs_list, settings=settings)




@app.route('/jobs', methods=['GET'])
def job_list():

    
    # Filtreleme kriterlerini al
    firma_adi = request.args.get('firma_adi')
    is_alani = request.args.get('is_alani')
    il = request.args.get('il')
    ilce = request.args.get('ilce')
    koy = request.args.get('koy')
    
    min_ucret = request.args.get('min_ucret', type=int)
    max_ucret = request.args.get('max_ucret', type=int)
    cinsiyet = request.args.get('cinsiyet')
    min_calisma_suresi = request.args.get('min_calisma_suresi', type=int)
    max_calisma_suresi = request.args.get('max_calisma_suresi', type=int)
    gereken_egitim = request.args.get('gereken_egitim')
    min_tecrube_sarti = request.args.get('min_tecrube_sarti', type=int)
    max_tecrube_sarti = request.args.get('max_tecrube_sarti', type=int)
    yas = request.args.get('yas', type=int)


    # MongoDB'den iş ilanlarını alıyoruz
    jobs = jobs_collection.find()
    filtered_jobs = list(jobs)  # MongoDB cursor'ını listeye dönüştür

    if firma_adi:
        filtered_jobs = [job for job in filtered_jobs if job['Firma Adi'].lower() == firma_adi.lower()]
    if is_alani:
        filtered_jobs = [job for job in filtered_jobs if job['Is Alani'].lower() == is_alani.lower()]
    if il:
        filtered_jobs = [job for job in filtered_jobs if job['Il'].lower() == il.lower()]
    if ilce:
        filtered_jobs = [job for job in filtered_jobs if job['Ilce'].lower() == ilce.lower()]
    if koy:
        filtered_jobs = [job for job in filtered_jobs if job['Koy'].lower() == koy.lower()]
    if min_ucret:
        filtered_jobs = [job for job in filtered_jobs if job['Ucret'] >= min_ucret]
    if max_ucret:
        filtered_jobs = [job for job in filtered_jobs if job['Ucret'] <= max_ucret]
    if cinsiyet:
        filtered_jobs = [job for job in filtered_jobs if job['Cinsiyet'] == cinsiyet]
    if min_calisma_suresi:
        filtered_jobs = [job for job in filtered_jobs if job['Calisma Surezi'] >= min_calisma_suresi]
    if max_calisma_suresi:
        filtered_jobs = [job for job in filtered_jobs if job['Calisma Surezi'] <= max_calisma_suresi]
    if gereken_egitim:
        filtered_jobs = [job for job in filtered_jobs if job['Gereken Egitim'] == gereken_egitim]
    if min_tecrube_sarti:
        filtered_jobs = [job for job in filtered_jobs if job['Tecrube sarti'] >= min_tecrube_sarti]
   
    if yas:
        jobs = []
        for job in filtered_jobs:
            min_age, max_age = job["Yas Siniri"].split("-")
            if int(min_age) <= yas <= int(max_age):
                jobs.append(job)
        filtered_jobs = jobs

    # MongoDB verisini JSON formatına çevir
    serialized_jobs = [ {key: serialize_objectid(value) for key, value in job.items()} for job in filtered_jobs ]
    return jsonify(serialized_jobs)

    





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


