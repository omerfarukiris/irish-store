from django.test import Client, TestCase
from django.urls import reverse

from .models import Product


class AddToCartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test ürün", description="Örnek", price="100.00",
            image="products/test.png", stock=5,
            category="erkek", product_type="gomlek",
        )
        self.url = reverse("store:add_to_cart", args=[self.product.pk])

    def test_add_replace_and_keep_cart_after_redirect(self):
        response = self.client.post(self.url, {"quantity": "2"}, follow=True)
        self.assertContains(response, "Sepetteki adet 2 olarak kaydedildi.")
        self.assertEqual(self.client.session["cart"], {str(self.product.pk): 2})
        self.client.post(self.url, {"quantity": "3"})
        self.assertEqual(self.client.session["cart"], {str(self.product.pk): 3})
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertNotIn("cart", Client().session)

    def test_invalid_quantities_do_not_change_cart(self):
        self.client.post(self.url, {"quantity": "2"})
        for quantity in (None, "", "abc", "1.5", "0", "-2", "6"):
            with self.subTest(quantity=quantity):
                data = {} if quantity is None else {"quantity": quantity}
                self.assertEqual(self.client.post(self.url, data).status_code, 400)
                self.assertEqual(self.client.session["cart"], {str(self.product.pk): 2})

    def test_unavailable_products_and_get_are_rejected(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.product.stock = 0
        self.product.save()
        self.assertEqual(self.client.post(self.url, {"quantity": "1"}).status_code, 400)
        self.product.is_active = False
        self.product.save()
        self.assertEqual(self.client.post(self.url, {"quantity": "1"}).status_code, 404)
        missing_url = reverse("store:add_to_cart", args=[self.product.pk + 100])
        self.assertEqual(self.client.post(missing_url, {"quantity": "1"}).status_code, 404)

    def test_form_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        detail_url = reverse("store:product_detail", args=[self.product.pk])
        response = client.get(detail_url)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertEqual(client.post(self.url, {"quantity": "1"}).status_code, 403)
        response = client.post(self.url, {
            "quantity": "1",
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })
        self.assertRedirects(response, detail_url)

    def test_cart_shows_size_quantity_and_current_price_total(self):
        self.client.post(self.url, {"quantity": "2", "size": "m"})
        self.product.price = "125.00"
        self.product.save()
        response = self.client.get(reverse("store:cart_detail"))
        self.assertContains(response, "Test ürün")
        self.assertContains(response, "Beden: M")
        self.assertContains(response, "Adet: 2")
        self.assertEqual(response.context["total"], 250)
        self.assertContains(Client().get(reverse("store:cart_detail")), "Sepetiniz henüz boş.")

    def test_invalid_size_does_not_modify_cart(self):
        response = self.client.post(self.url, {"quantity": "2", "size": "fake"})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("cart", self.client.session)

    def test_cart_badge_and_feedback_follow_total_quantity(self):
        response = self.client.get(reverse("store:index"))
        self.assertContains(response, 'class="cart-badge">0</span>')
        response = self.client.post(self.url, {"quantity": "3", "size": "m"}, follow=True)
        self.assertContains(response, 'class="cart-badge">3</span>')
        self.assertContains(response, "Sepeti görüntüle · 3 adet")
        self.assertContains(response, 'role="status"')
        self.client.post(self.url, {"quantity": "2"})
        response = self.client.get(reverse("store:cart_detail"))
        self.assertContains(response, 'class="cart-badge">2</span>')
        self.assertContains(response, "1 farklı ürün · 2 adet")


class StoreFlowTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='customer', password='Test-password-408!')
        self.product = Product.objects.create(name='Keten gömlek', description='Rahat', price='120.00', image='test.png', stock=4, category='erkek', product_type='gomlek')

    def test_search_sort_and_empty_results(self):
        url = reverse('store:product_list')
        response = self.client.get(url, {'q': 'Keten', 'sort': 'price_asc'})
        self.assertContains(response, 'Keten gömlek')
        response = self.client.get(url, {'q': 'no-match'})
        self.assertContains(response, 'Seçtiğiniz filtrelere uygun ürün bulunamadı.')
        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_login_preserves_cart_update_and_remove(self):
        self.client.post(reverse('store:add_to_cart', args=[self.product.pk]), {'quantity': '2'})
        self.client.post(reverse('store:login'), {'username': 'customer', 'password': 'Test-password-408!'})
        self.assertEqual(self.client.session['cart'][str(self.product.pk)], 2)
        self.client.post(reverse('store:update_cart', args=[self.product.pk]), {'quantity': '3'})
        self.assertEqual(self.client.session['cart'][str(self.product.pk)], 3)
        self.client.post(reverse('store:update_cart', args=[self.product.pk]), {'quantity': '99'})
        self.assertEqual(self.client.session['cart'][str(self.product.pk)], 3)
        self.client.post(reverse('store:remove_from_cart', args=[self.product.pk]))
        self.assertEqual(self.client.session['cart'], {})

    def test_checkout_stock_snapshot_replay_and_ownership(self):
        from .models import Order
        self.client.force_login(self.user)
        self.client.post(reverse('store:add_to_cart', args=[self.product.pk]), {'quantity': '2', 'size': 'm'})
        self.client.get(reverse('store:checkout'))
        data = {'token': self.client.session['checkout_token'], 'full_name': 'Örnek Kullanıcı', 'address': 'Örnek adres'}
        response = self.client.post(reverse('store:checkout'), data)
        order = Order.objects.get()
        self.assertRedirects(response, reverse('store:order_detail', args=[order.pk]))
        self.assertEqual(order.total, 240)
        self.assertEqual(order.items.get().size, 'm')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
        self.assertEqual(self.client.session['cart'], {})
        self.client.post(reverse('store:checkout'), data)
        self.assertEqual(Order.objects.count(), 1)
        self.client.post(reverse('store:add_to_cart', args=[self.product.pk]), {'quantity': '1'})
        data['token'] = self.client.session['checkout_token']
        self.client.post(reverse('store:checkout'), data)
        self.assertEqual(Order.objects.count(), 2)
        other = Client()
        from django.contrib.auth.models import User
        other.force_login(User.objects.create_user(username='other'))
        self.assertEqual(other.get(reverse('store:order_detail', args=[order.pk])).status_code, 404)

    def test_insufficient_stock_rolls_back_order(self):
        from .models import Order
        self.client.force_login(self.user)
        self.client.post(reverse('store:add_to_cart', args=[self.product.pk]), {'quantity': '4'})
        self.product.stock = 1
        self.product.save()
        self.client.get(reverse('store:checkout'))
        response = self.client.post(reverse('store:checkout'), {'token': self.client.session['checkout_token'], 'full_name': 'Örnek', 'address': 'Örnek adres'})
        self.assertContains(response, 'yeterli stok yok')
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

    def test_auth_pages_and_registration(self):
        for name in ('login', 'register'):
            self.assertEqual(self.client.get(reverse('store:' + name)).status_code, 200)
        self.assertEqual(self.client.get(reverse('store:account')).status_code, 302)
        response = self.client.post(reverse('store:register'), {'first_name': 'Örnek', 'last_name': 'Kullanıcı', 'email': 'new@example.com', 'username': 'newcustomer', 'password1': 'Safe-new-pass-840!', 'password2': 'Safe-new-pass-840!'})
        self.assertRedirects(response, reverse('store:account'))
        self.assertFalse(response.wsgi_request.user.is_staff)
        self.assertEqual(self.client.get(reverse('store:logout')).status_code, 405)


class RegistrationTests(TestCase):
    def data(self, **changes):
        data = {'first_name': 'İpek', 'last_name': 'Yılmaz', 'email': 'Ipek@example.com', 'username': 'ipek', 'password1': 'Secure-840-new!', 'password2': 'Secure-840-new!'}
        data.update(changes)
        return data

    def test_details_saved_password_hashed_and_cart_preserved(self):
        from django.contrib.auth.models import User
        session = self.client.session
        session['cart'] = {'7': 2}
        session.save()
        response = self.client.post(reverse('store:register'), self.data())
        self.assertRedirects(response, reverse('store:account'))
        user = User.objects.get(username='ipek')
        self.assertEqual((user.first_name, user.last_name, user.email), ('İpek', 'Yılmaz', 'ipek@example.com'))
        self.assertTrue(user.check_password('Secure-840-new!'))
        self.assertFalse(user.is_staff)
        self.assertEqual(self.client.session['cart'], {'7': 2})
        self.assertContains(self.client.get(reverse('store:account')), 'İpek Yılmaz')

    def test_required_fields_and_invalid_password_do_not_create_users(self):
        from django.contrib.auth.models import User
        for changes in ({'first_name': ''}, {'last_name': '  '}, {'email': 'invalid'}, {'password2': 'different'}):
            with self.subTest(changes=changes):
                response = self.client.post(reverse('store:register'), self.data(**changes))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='ipek').exists())

    def test_duplicate_email_is_rejected_ignoring_case(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='existing', email='IPEK@example.com')
        response = self.client.post(reverse('store:register'), self.data())
        self.assertIn('email', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='ipek').exists())
