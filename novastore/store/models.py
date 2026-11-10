from django.db import models

CATEGORY_CHOICES = [
    ("erkek", "Erkek"),
    ("kadin", "Kadın"),
    ("aksesuar", "Aksesuar"),
]

PRODUCT_TYPE_CHOICES = [
    ("gomlek", "Gömlek"),
    ("tisort", "Tişört"),
    ("pantolon", "Pantolon"),
    ("kazak", "Kazak"),
    ("hirka", "Hırka"),
    ("sweatshirt", "Sweatshirt"),
    ("ceket", "Ceket"),
    ("mont", "Mont"),
    ("elbise", "Elbise"),
    ("etek", "Etek"),
    ("sort", "Şort"),
    ("canta", "Çanta"),
    ("sal", "Şal"),
    ("gozluk", "Güneş Gözlüğü"),
    ("kemer", "Kemer"),
    ("sapka", "Şapka"),
    ("overshirt", "Gömlek Ceket"),
    ("bluz", "Bluz"),
    ("polo", "Polo Tişört"),
    ("atlet", "Atlet"),
    ("yelek", "Yelek"),
    ("kaban", "Kaban"),
    ("trenckot", "Trençkot"),
    ("jean", "Jean"),
    ("tayt", "Tayt"),
    ("esofman_alti", "Eşofman Altı"),
    ("tulum", "Tulum"),
    ("takim_elbise", "Takım Elbise"),
    ("atki", "Atkı"),
    ("bere", "Bere"),
    ("eldiven", "Eldiven"),
    ("cuzdan", "Cüzdan"),
    ("kravat", "Kravat"),
    ("taki", "Takı"),
]


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
    )
    product_type = models.CharField(
        max_length=30,
        choices=PRODUCT_TYPE_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='store_orders')
    full_name = models.CharField(max_length=120)
    address = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(unique=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=20, blank=True)
