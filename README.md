# Irısh Store

[![Django checks](https://github.com/omerfarukiris/irish-store/actions/workflows/tests.yml/badge.svg)](https://github.com/omerfarukiris/irish-store/actions/workflows/tests.yml)


Django ile geliştirilmiş, Türkçe arayüzlü bir e-ticaret öğrenme projesi. Ürün keşfinden sepete ve deneme siparişine kadar alışveriş akışını kapsar.

**Durum:** Yerel deneme sürümü. Gerçek ödeme alınmaz ve ürün gönderilmez.

## Kullanılan teknolojiler

| Katman | Teknoloji |
| --- | --- |
| Backend | Python 3.12, Django 5.2 |
| Arayüz | Django Templates, HTML, CSS, JavaScript |
| Varsayılan veritabanı | SQLite |
| Alternatif veritabanı | MySQL (`mysqlclient` ile) |
| Ortam ayarları | `.env`, python-dotenv |
| Otomatik kontroller | Django TestCase, GitHub Actions |

## Yerel kurulum

Komutları proje kökünde çalıştırın. Aşağıdaki örnekler macOS/Linux içindir.

### 1. Ortamı ve paketleri hazırlayın

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Mevcut bir `.env` dosyanız varsa üzerine kopyalamayın.

### 2. Gizli anahtarı ayarlayın

```sh
.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Çıktıyı `.env` dosyasındaki `DJANGO_SECRET_KEY` alanına **tek tırnak içinde** yazın. Örnek dosyadaki yer tutucuyla uygulama başlamaz. Anahtarı paylaşmayın.

`.env` proje kökünden otomatik okunur; sistem ortam değişkenleri önceliklidir. İlk kurulumda `DB_ENGINE=sqlite` bırakılabilir.

### 3. Tabloları ve yönetici hesabını oluşturun

```sh
.venv/bin/python novastore/manage.py migrate
.venv/bin/python novastore/manage.py createsuperuser
```

### 4. Uygulamayı başlatın

```sh
bash script.sh
```

Alternatif:

```sh
.venv/bin/python novastore/manage.py runserver
```

- Mağaza: [localhost:8000](http://127.0.0.1:8000/)
- Yönetim paneli: [localhost:8000/admin](http://127.0.0.1:8000/admin/)

Yeni kurulum ürün verisi içermez. Yönetim panelinden ürün, fiyat, stok ve görselleri ekleyin. Mevcut yerel veritabanı ve görseller silinmez. “Yeni Gelenler” yalnızca son 30 günde eklenen aktif ürünleri gösterir.

Windows'ta `.venv/bin/python` yerine `.venv\Scripts\python.exe` kullanın; `.env.example` dosyasını `.env` adıyla kopyalayın ve `runserver` komutuyla başlatın.

## Özellikler

- Responsive ana sayfa, kategori menüsü ve ürün detayları.
- Ürün arama, kategori/tür filtreleri, fiyat/tarih sıralaması, filtreleri koruyan sayfalama.
- Misafir sepeti, toplam adet rozeti, beden tercihi, adet güncelleme ve kaldırma.
- Ad, soyad, e-posta, kullanıcı adı ve şifre doğrulamalı kayıt; giriş, POST ile çıkış, hesap bilgileri ve sipariş geçmişi.
- Giriş sırasında sepet korunur. Çıkış yapıldığında oturum ve sepet temizlenir.
- Ödeme almadan deneme siparişi; sipariş anındaki ad/fiyat/beden bilgileri saklanır.
- Transaction içinde koşullu stok azaltma, stok yetersizliğinde geri alma ve tekrar gönderime karşı benzersiz sipariş anahtarı.
- Siparişler yalnızca sahipleri tarafından görüntülenir.

## Bu projede neler öğrendik?

Bu proje, yalnızca sayfa tasarlamayı değil, tarayıcıdan gelen bir isteğin veritabanına ve tekrar kullanıcıya uzanan akışını uygulamak için geliştirildi. Aşağıdaki konular proje içinde örneklendi; her birini bağımsız uygulayabilmek tekrar ve pratik gerektirir.

### Python temelleri

- Değişkenler, fonksiyonlar, parametreler ve `return` ile veri ve işlem akışını yönetme.
- Girintinin blokları nasıl belirlediğini; `if` / `elif` ile adet ve stok kontrolü yapmayı anlama.
- `int()` ile formdan gelen metni sayıya çevirme; `try` / `except` ile eksik veya hatalı değerleri karşılama.
- Sözlüklerde ürün ID'sini anahtar, adedi değer olarak saklama; `str()` ile ID'yi metne dönüştürme.
- Parasal hesaplamalarda `Decimal` kullanma.

### Django ve web akışı

- `URL → view → model → template → yanıt` akışını kurma.
- `GET` ile sayfa/veri isteme; `POST` ile sepet, hesap ve sipariş gibi değişiklikleri gönderme.
- `request.GET`, `request.POST` ve `request.session` arasındaki farkı görme.
- `get_object_or_404()` ile ürün bulma, `render()` ile HTML oluşturma, `redirect()` ile işlem sonrası yönlendirme.
- `400`, `403`, `404` ve `405` yanıtlarının farklı hata durumlarını ifade ettiğini öğrenme.

### Veritabanı ve Django ORM

- `Product`, `Order` ve `OrderItem` modellerini oluşturma; `ForeignKey` ile kullanıcı, sipariş ve ürün ilişkilerini kurma.
- `filter()`, `Q`, `order_by()` ve tarih koşullarıyla ürün arama, filtreleme ve sıralama.
- Migration dosyalarıyla tablo yapısını değiştirme; migration'ın mevcut verileri başka bir veritabanına taşımadığını anlama.
- Admin panelinden ürün yönetme ve sipariş kayıtlarını inceleme.
- SQLite ile dosya tabanlı çalışma; MySQL için sürücü ve bağlantı yapılandırması hazırlama. Gerçek MySQL sunucusuyla yerel bağlantı henüz doğrulanmadı.

### Formlar ve kullanıcı hesapları

- Django formlarıyla zorunlu alanları, e-posta biçimini ve şifre tekrarını doğrulama.
- Hazır `UserCreationForm` yapısını ad, soyad ve e-posta alanlarıyla genişletme.
- Kayıtlı e-posta için form düzeyinde kontrol yapma ve hataları ilgili alanın yanında gösterme.
- Django'nun şifreleri hashleyerek saklamasını kullanma; kayıt, giriş ve POST ile çıkış akışlarını kurma.
- `login_required` ve kullanıcıya göre sorgulama ile hesap ve sipariş erişimini sınırlama.

### Sepet ve sipariş mantığı

- Giriş yapmamış ziyaretçinin sepetini session içinde saklama; yerel değişken ile kalıcı oturum verisi arasındaki farkı görme.
- Ürün/adet bilgisini kaydetme, güncelleme ve kaldırma; beden tercihini saklama.
- Context processor ile toplam ürün adedini ortak navbar üzerinde gösterme.
- Fiyatı tarayıcıdan almak yerine veritabanından hesaplama; siparişte ürün adı ve fiyatının o anki kopyasını saklama.
- `transaction.atomic()` ve koşullu stok güncellemesiyle, stok yetersizse sipariş işlemini geri alma.
- Benzersiz sipariş anahtarıyla aynı formun tekrar gönderilmesinin siparişi çoğaltmasını engelleme.

### Arayüz ve kullanıcı deneyimi

- Template kalıtımıyla ortak navbar, footer ve mesaj alanlarını `base.html` içinde toplama.
- CSS Grid, Flexbox ve media query ile farklı ekran boyutlarına uyarlama.
- Mobil menü, seçili kategori, boş sonuç ve boş sepet durumlarını tasarlama.
- Form etiketleri, klavye odak göstergeleri ve durum mesajlarıyla erişilebilirliği iyileştirme.
- Butonlarda metin/zemin kontrastını düzeltme; sayfalama sırasında filtreleri koruma.

### Test, yapılandırma ve GitHub hazırlığı

- Django test istemcisiyle form gönderme, yanıtları ve session verilerini kontrol etme.
- Geçersiz adet, stok aşımı, şifre uyuşmazlığı, sipariş sahipliği ve tekrar gönderim gibi hata senaryolarını test etme.
- Gizli anahtar ve bağlantı bilgilerini `.env` dosyasına taşıma; `.env.example` ile paylaşılabilir bir şablon hazırlama.
- `.gitignore` ile gizli bilgileri, yerel veritabanını ve yüklenen dosyaları depodan dışlama.
- Kurulum ve kullanım adımlarını README'de belgeleme; GitHub Actions için SQLite ve MySQL test akışları hazırlama.

### Henüz kapsamda olmayan konular

Gerçek ödeme entegrasyonu, e-posta doğrulama, şifre sıfırlama, bedenlere göre ayrı stok ve canlı sunucuya dağıtım bu projede tamamlanmış öğrenme başlıkları değildir.

## Kullanım akışı

1. Koleksiyonda ürün arayın, filtreleyin ve detayını açın.
2. Beden ve adet seçerek sepete ekleyin. Aynı ürün tekrar eklenirse seçim güncellenir.
3. Sepette adedi değiştirin veya ürünü kaldırın.
4. Deneme siparişi için kayıt olun ya da kullanıcı adınızla giriş yapın.
5. Örnek teslimat bilgileriyle siparişi tamamlayın; sonuç hesabınızda listelenir.

Sipariş stoktan düşer. E-posta kaydedilir fakat doğrulama e-postası gönderilmez.

## Proje yapısı

```text
.
├── .env.example             # Paylaşılabilir ortam şablonu
├── .github/workflows/       # SQLite ve MySQL test akışları
├── novastore/
│   ├── manage.py
│   ├── novastore/           # Django ayarları ve ana URL'ler
│   ├── store/               # Modeller, formlar, view'lar, testler
│   │   ├── migrations/
│   │   ├── templates/store/
│   │   └── static/store/
│   ├── templates/base.html  # Navbar, mesajlar ve footer
│   └── static/css/          # Ortak stiller
├── requirements.txt
├── requirements-mysql.txt
└── script.sh
```

## Ortam değişkenleri

| Değişken | Amaç |
| --- | --- |
| `DJANGO_SECRET_KEY` | Zorunlu, kişiye/ortama özel gizli anahtar |
| `DJANGO_DEBUG` | Yerelde `true`, yayında `false` |
| `DJANGO_ALLOWED_HOSTS` | Virgülle ayrılan host adları; protokol içermez |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Gerektiğinde protokol içeren güvenilir kökenler |
| `DB_ENGINE` | `sqlite` veya `mysql` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL veritabanı ve bağlantı bilgileri |
| `DB_HOST`, `DB_PORT` | MySQL adresi ve portu |

## Kontroller

```sh
.venv/bin/python novastore/manage.py test store
.venv/bin/python novastore/manage.py check
```

## Sınırlar

Yerel deneme sürümüdür; üretim yayını yapılmadı. Gerçek ödeme, gönderim, e-posta, şifre sıfırlama ve bedenlere göre ayrı stok içermez. Aynı ürün yeniden eklendiğinde adet ve beden son seçimle değiştirilir; farklı bedenler ayrı kalem olmaz. Örnek teslimat bilgisi kullanın. Kargo ücreti hesaplanmaz.

Yayın için ayrı ortam ayarları, gizli anahtar, DEBUG kapatma, uygun host/HTTPS ve veri saklama yapılandırması gerekir. Geliştirme sunucusunu internete açmayın.


## MySQL / phpMyAdmin

Django MySQL'e Python sürücüsüyle doğrudan bağlanır. PHP gerekmez; phpMyAdmin aynı sunucudaki veritabanını görüntülemek ve yönetmek için kullanılabilir. Yalnızca PHP çalıştıran bir hosting Django uygulamasını çalıştırmaya yetmez.

1. MySQL sunucusunu ve `mysqlclient` derleme araçlarını kurun. macOS'ta Homebrew ile `mysql-client` ve `pkg-config` gerekir; MySQL sunucusunun ayrıca çalışıyor olması gerekir. Windows/macOS için sürücünün kurulum yönergelerine bakın: https://github.com/PyMySQL/mysqlclient
2. Bir yönetici hesabıyla boş veritabanı ve ayrı uygulama kullanıcısı oluşturun. Aşağıdaki şifre yalnızca yer tutucudur; çalıştırmadan önce değiştirin. Host kısmını bağlantı ortamınıza göre ayarlayın:

```sql
CREATE DATABASE irish_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'irish_app'@'localhost' IDENTIFIED BY 'CHANGE-THIS-PASSWORD';
GRANT ALL PRIVILEGES ON irish_store.* TO 'irish_app'@'localhost';
```

3. Sürücüyü kurun:

```sh
.venv/bin/python -m pip install -r requirements-mysql.txt
```

4. `.env` içindeki bağlantı ayarlarını değiştirin:

```dotenv
DB_ENGINE=mysql
DB_NAME=irish_store
DB_USER=irish_app
DB_PASSWORD='your-actual-password'
DB_HOST=127.0.0.1
DB_PORT=3306
```

5. Tabloları oluşturup bağlantıyı kontrol edin:

```sh
.venv/bin/python novastore/manage.py check --database default
.venv/bin/python novastore/manage.py migrate
.venv/bin/python novastore/manage.py createsuperuser
```

`migrate` tabloları oluşturur, SQLite verilerini taşımaz. Yeni MySQL veritabanı başlangıçta boş olacaktır. SQLite dosyası değiştirilmez. MySQL'e geçmeden önce mevcut verilerinizi yedekleyin; aktarma gerekiyorsa ayrıca planlayın. Görseller `novastore/media/` klasöründedir ve ayrı taşınır.

Yerel MySQL testi için ayrı test veritabanı oluşturma/silme yetkisi gerekir; normal uygulama kullanıcısının yetkisini genişletmek yerine ayrı test kullanıcısı kullanın. GitHub Actions bu testleri izole MySQL servisiyle çalıştırır. MySQL yapılandırması yerelde gerçek sunucuyla henüz doğrulanmamıştır.

## GitHub'a yükleme

`.env.example` paylaşılır; `.env`, SQLite dosyaları, medya yüklemeleri ve `backups/` paylaşılmaz. Ürün görsellerinin statik tasarım dosyaları depoya dahildir. Kullanıcı, sipariş ve ürün veritabanı kayıtları depoya dahil değildir.

```sh
git status --short
git add .
git diff --cached --stat
git commit -m "Prepare Irish Store Django demo"
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Göndermeden önce `.env` dosyasının dışlandığını kontrol edin:

```sh
git check-ignore .env novastore/db.sqlite3
```

`.github/workflows/tests.yml`, push ve pull request sırasında SQLite ve MySQL üzerinde kontrolleri çalıştırır. CI içindeki örnek anahtar ve şifreler yalnızca geçici test servisleri içindir; gerçek hesabınızın bilgileri değildir.

## Yayın ayarları

GitHub'a kod yüklemek uygulamayı yayınlamaz. Yayında `DJANGO_DEBUG=false`, güçlü `DJANGO_SECRET_KEY`, gerçek `DJANGO_ALLOWED_HOSTS` ve HTTPS kökenleri için `DJANGO_CSRF_TRUSTED_ORIGINS` ayarlanmalıdır. Statik dosyalar `collectstatic` ile hazırlanır; medya, HTTPS ve uygulama sunucusu hosting ortamında ayrıca yapılandırılır.

```sh
.venv/bin/python novastore/manage.py collectstatic --noinput
.venv/bin/python novastore/manage.py check --deploy
```

Django veritabanı belgeleri: https://docs.djangoproject.com/en/5.2/ref/databases/#mysql-notes
