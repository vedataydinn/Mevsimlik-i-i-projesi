from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from elasticsearch import Elasticsearch
from pymongo import MongoClient
import joblib
from bson import ObjectId
import numpy as np
from functools import wraps
import secrets



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Güvenli bir secret key

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


"""joblib.load("isci_ilan_modeli.pkl")
scaler = joblib.load("isci_ilan_scaler.pkl")
label_encoders = joblib.load("isci_ilan_label_encoders.pkl")
        return model, scaler, label_encoders

# Load Model and Scaler
model, scaler, label_encoders = ModelFactory.load_model()

"""
def load_model():
    """
    Model, scaler ve label encoder dosyalarını yükler.
    """
    try:
        model = joblib.load("isci_ilan_modeli.pkl")
        scaler = joblib.load("isci_ilan_scaler.pkl")
        label_encoders = joblib.load("isci_ilan_label_encoders.pkl")
        return model, scaler, label_encoders
    except FileNotFoundError as e:
        print(f"Model dosyası bulunamadı: {e}")
        raise
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        raise

# Model ve diğer dosyaları yükle
try:
    model, scaler, label_encoders = load_model()
    print("Model ve diğer dosyalar başarıyla yüklendi.")
except Exception as e:
    print(f"Hata: {e}")

# ObjectId'yi JSON uyumlu hale getirme
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('loginPage'))
        return f(*args, **kwargs)
    return decorated_function

# Ana sayfa route'u
@app.route('/')
@login_required
def index():
    try:
        jobs = jobs_collection.find()
        jobs_list = list(jobs)
        jobs_list = [serialize_objectid(job) for job in jobs_list]
        settings = {"isShowFilterMode": True}
        is_logged_in = 'user_id' in session
    except Exception as e:
        print("Veritabanı hatası:", e)
        jobs_list = []
        settings = {"isShowFilterMode": False}
        is_logged_in = False

    return render_template('index.html', jobs=jobs_list, settings=settings, is_logged_in=is_logged_in)



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
@login_required 
def ilanVer():
    return render_template('ilan-Ver.html')


@app.route('/loginPage', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Kullanıcı doğrulama
        user = mongo_db.workers.find_one({'email': email})
        if user is None:
            user = mongo_db.workers.find_one({'E-Posta': email})
        if user is None:
            user = mongo_db.employers.find_one({'email': email})
        if user is None:
            user = mongo_db.employers.find_one({'E-Posta': email})
            
            
        if user:
            if  "password" in user:
                db_password = user["password"]
            elif "Şifre" in user:
                db_password = user["Şifre"]

            if db_password == password:
                session['user_id'] = str(user['_id'])
                return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Geçersiz email veya şifre'}), 401
            
    return render_template('loginPage.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('loginPage'))

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





@app.route('/jobs', methods=['GET'])
def job_list():
    # Arama sorgusu ve tüm filtre parametrelerini al
    search_query = request.args.get('search_query', '').lower()
    
    # Diğer filtre parametrelerini al
    firma_adi = request.args.get('firma_adi')
    is_alani = request.args.get('is_alani')
    il = request.args.get('il')
    ilce = request.args.get('ilce')
    koy = request.args.get('koy')
    min_ucret = request.args.get('min_ucret')
    max_ucret = request.args.get('max_ucret')
    
    min_ucret = request.args.get('min_ucret', type=int)
    max_ucret = request.args.get('max_ucret', type=int)
    cinsiyet = request.args.get('cinsiyet')
    min_calisma_suresi = request.args.get('min_calisma_suresi', type=int)
    max_calisma_suresi = request.args.get('max_calisma_suresi', type=int)
    gereken_egitim = request.args.get('gereken_egitim')
    min_tecrube_sarti = request.args.get('min_tecrube_sarti', type=int)
    max_tecrube_sarti = request.args.get('max_tecrube_sarti', type=int)
    yas = request.args.get('yas', type=int)
    # Seçim kutusu (select) filtreleri
    konaklama = request.args.get('konaklama')
    tecrube_sarti = request.args.get('tecrube_sarti')
    sigorta = request.args.get('sigorta')
    
    # MongoDB'den iş ilanlarını al
    jobs = jobs_collection.find()
    filtered_jobs = list(jobs)
    filtered_jobs = [serialize_objectid(job) for job in filtered_jobs]

    # Arama sorgusu filtrelemesi
    if search_query:
        filtered_jobs = [job for job in filtered_jobs if any([
            search_query in str(job.get('Il', '')).lower(),
            search_query in str(job.get('Ilce', '')).lower(),
            search_query in str(job.get('Koy', '')).lower(),
            search_query in str(job.get('Firma Adi', '')).lower(),
            search_query in str(job.get('Is Alani', '')).lower()
        ])]

    # Diğer filtreleri uygula
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
    if max_tecrube_sarti:
        filtered_jobs = [job for job in filtered_jobs if job['Tecrube sarti'] <= max_tecrube_sarti]
    if yas:
        jobs = []
        for job in filtered_jobs:
            min_age, max_age = job["Yas Siniri"].split("-")
            if min_age <= yas and yas <= max_age:
                jobs.append(job)
        filtered_jobs = jobs 

    # Select box filtreleri
    if konaklama:
        filtered_jobs = [job for job in filtered_jobs 
                        if str(job.get('Konaklama', '')).strip().lower() == konaklama.strip().lower()]
    
    if tecrube_sarti:
        tecrube_sarti = int(tecrube_sarti)
        filtered_jobs = [job for job in filtered_jobs 
                        if int(str(job.get('Tecrube Sarti', '0')).strip()) == tecrube_sarti]
    
    if sigorta:
        filtered_jobs = [job for job in filtered_jobs 
                        if str(job.get('Sigorta', '')).strip().lower() == sigorta.strip().lower()]

    settings = {
        "isShowFilterMode": True
    }
    
    is_logged_in = 'user_id' in session
    return render_template("index.html", jobs=filtered_jobs, settings=settings, is_logged_in=is_logged_in)











@app.route('/job_match', methods=['GET', 'POST'])
def job_match():
    if request.method == 'POST':
        try:
            worker_data = {
                "Yaş": int(request.form.get("yas")),
                "Eğitim": request.form.get("egitim"),
                "Deneyim (Yıl)": int(request.form.get("deneyim")),
                "Şehir": request.form.get("sehir"),
                "İlçe": request.form.get("ilce"),
                "Tercih Edilen İş Alanları": request.form.get("isAlanlari"),
                "Ücret Beklentisi": int(request.form.get("ucretBeklentisi"))
            }

            workers_collection.insert_one(worker_data)

            worker_input = np.array([[worker_data['Yaş'], worker_data['Eğitim'], worker_data['Deneyim (Yıl)'],
                                      worker_data['Ücret Beklentisi'], worker_data['Tercih Edilen İş Alanları'],
                                      worker_data['Şehir'], worker_data['İlçe']]])
            worker_input_scaled = scaler.transform(worker_input)

            jobs = jobs_collection.find()
            job_matches = []

            for job in jobs:
                job_input = np.array([[job['Yas Sınırı'], job['Gereken Eğitim'], job['Tecrube Sarti'],
                                       job['Ucret'], job['Is Alani'], job['Il'], job['Ilce']]])
                job_input_scaled = scaler.transform(job_input)
                score = model.predict(job_input_scaled)
                job_matches.append({'job': job, 'score': score[0]})

            job_matches = sorted(job_matches, key=lambda x: x['score'], reverse=True)
            top_10_jobs = job_matches[:10]

            return render_template('job_matches.html', jobs=top_10_jobs)

        except Exception as e:
            print(f"Hata: {e}")
            return "Bir hata oluştu.", 500

    return render_template('job_match_form.html')




def serialize_objectid(job):
    """MongoDB ObjectId'yi JSON uyumlu bir yapıya çevirir."""
    job["_id"] = str(job["_id"])  # ObjectId'yi string'e dönüştür
    return job






















"""
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
    return jsonify(response)"""


if __name__ == '__main__':
    app.run(debug=True)


