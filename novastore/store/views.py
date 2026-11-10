from datetime import timedelta
from decimal import Decimal
import uuid

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models import Q, F
from .forms import CheckoutForm, RegistrationForm
from .models import Order, OrderItem

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Value, When
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import CATEGORY_CHOICES, PRODUCT_TYPE_CHOICES, Product

# Create your views here.


def apply_product_order(queryset):
    return queryset.annotate(
        category_order=Case(
            When(category="erkek", then=Value(1)),
            When(category="kadin", then=Value(2)),
            When(category="aksesuar", then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        ),
        type_order=Case(
            When(product_type="gomlek", then=Value(1)),
            When(product_type="tisort", then=Value(2)),
            When(product_type="pantolon", then=Value(3)),
            When(product_type="kazak", then=Value(4)),
            When(product_type="hirka", then=Value(5)),
            When(product_type="sweatshirt", then=Value(6)),
            When(product_type="ceket", then=Value(7)),
            When(product_type="mont", then=Value(8)),
            When(product_type="elbise", then=Value(9)),
            When(product_type="etek", then=Value(10)),
            When(product_type="sort", then=Value(11)),
            When(product_type="canta", then=Value(12)),
            When(product_type="sal", then=Value(13)),
            When(product_type="gozluk", then=Value(14)),
            When(product_type="kemer", then=Value(15)),
            When(product_type="sapka", then=Value(16)),
            When(product_type="overshirt", then=Value(17)),
            When(product_type="bluz", then=Value(18)),
            When(product_type="polo", then=Value(19)),
            When(product_type="atlet", then=Value(20)),
            When(product_type="yelek", then=Value(21)),
            When(product_type="kaban", then=Value(22)),
            When(product_type="trenckot", then=Value(23)),
            When(product_type="jean", then=Value(24)),
            When(product_type="tayt", then=Value(25)),
            When(product_type="esofman_alti", then=Value(26)),
            When(product_type="tulum", then=Value(27)),
            When(product_type="takim_elbise", then=Value(28)),
            When(product_type="atki", then=Value(29)),
            When(product_type="bere", then=Value(30)),
            When(product_type="eldiven", then=Value(31)),
            When(product_type="cuzdan", then=Value(32)),
            When(product_type="kravat", then=Value(33)),
            When(product_type="taki", then=Value(34)),
            default=Value(35),
            output_field=IntegerField(),
        ),
    ).order_by("category_order", "type_order", "-created_at", "-id")


def index(request):
    latest_products = (
        Product.objects.filter(
            is_active=True, created_at__gte=timezone.now() - timedelta(days=30)
        )
        .order_by("-created_at", "-id")
        .values_list("id", flat=True)[:12]
    )
    products = apply_product_order(
        Product.objects.filter(is_active=True, id__in=latest_products)
    )

    return render(request, "store/index.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
    )
    return render(request, "store/product_detail.html", {"product": product})


def new_arrivals(request):
    products = Product.objects.filter(
        is_active=True, created_at__gte=timezone.now() - timedelta(days=30)
    )
    return render_product_list(request, products, "Yeni Gelenler", "store:new_arrivals")


def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render_product_list(request, products, "Tüm Ürünler", "store:product_list")


def render_product_list(request, products, page_title, list_url_name):
    selected_category = request.GET.get("selected_category")

    selected_type = request.GET.get("selected_type")

    if selected_category and selected_category not in dict(CATEGORY_CHOICES):
        raise Http404("Kategori bulunamadı.")

    if selected_type and selected_type not in dict(PRODUCT_TYPE_CHOICES):
        raise Http404("Kategori Bulunamadı.")

    if selected_category:
        products = products.filter(category=selected_category)

    if selected_type:
        products = products.filter(product_type=selected_type)

    query = request.GET.get("q", "").strip()[:100]
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    sort = request.GET.get("sort", "recommended")
    orders = {"price_asc": "price", "price_desc": "-price", "newest": "-created_at"}
    products = products.order_by(orders[sort], "-pk") if sort in orders else apply_product_order(products)
    params = request.GET.copy()
    params.pop("page", None)

    paginator = Paginator(products, 16)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "store/new_arrivals.html",
        {
            "page_title": page_title,
            "query": query, "sort": sort, "filter_query": params.urlencode(),
            "list_url_name": list_url_name,
            "products": page_obj,
            "selected_category": selected_category,
            "selected_type": selected_type,
            "product_type_choices": PRODUCT_TYPE_CHOICES,
            "page_obj": page_obj,
        },
    )


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
    )

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity"))
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Adet geçerli bir tam sayı olmalıdır.")

        if quantity < 1:
            return HttpResponseBadRequest("Adet en az 1 olmalıdır!")
        elif quantity > product.stock:
            return HttpResponseBadRequest("Yeterli Kadar Stok Yoktur")

        cart = request.session.get("cart", {})
        size = request.POST.get("size", "")
        allowed_sizes = ("standart",) if product.category == "aksesuar" else ("s", "m", "l", "xl", "xxl")
        if size and size not in allowed_sizes:
            return HttpResponseBadRequest("Geçersiz beden seçimi.")
        sizes = request.session.get("cart_sizes", {})
        sizes[str(product_id)] = size
        request.session["cart_sizes"] = sizes
        cart[str(product_id)] = quantity
        request.session["cart"] = cart
        messages.success(
            request, f"{product.name}: Sepetteki adet {quantity} olarak kaydedildi."
        )
        return redirect("store:product_detail", product_id=product_id)


def cart_detail(request):
    cart = request.session.get("cart", {})
    sizes = request.session.get("cart_sizes", {})
    items = []
    total = Decimal("0.00")
    products = list(Product.objects.filter(pk__in=cart.keys()))
    present = {str(product.pk) for product in products}
    if set(cart) != present:
        cart = {key: value for key, value in cart.items() if key in present}
        request.session["cart"] = cart
        request.session["cart_sizes"] = {key: value for key, value in sizes.items() if key in present}
    for product in products:
        quantity = cart[str(product.pk)]
        subtotal = product.price * quantity
        items.append({
            "product": product,
            "quantity": quantity,
            "size": sizes.get(str(product.pk), "").upper(),
            "subtotal": subtotal,
            "unavailable": not product.is_active or quantity > product.stock,
        })
        total += subtotal
    return render(request, "store/cart.html", {"items": items, "total": total})


@require_POST
def remove_from_cart(request, product_id):
    for key in ("cart", "cart_sizes"):
        data = request.session.get(key, {})
        data.pop(str(product_id), None)
        request.session[key] = data
    messages.success(request, "Ürün sepetinizden kaldırıldı.")
    return redirect("store:cart_detail")


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", ""))
        if not 1 <= quantity <= product.stock:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(request, "Lütfen stok miktarını aşmayan, en az 1 adet girin.")
        return redirect("store:cart_detail")
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        cart[str(product_id)] = quantity
        request.session["cart"] = cart
        messages.success(request, "Sepetiniz güncellendi.")
    return redirect("store:cart_detail")


def register(request):
    if request.user.is_authenticated:
        return redirect("store:account")
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Hesabınız oluşturuldu. Hoş geldiniz!")
        return redirect("store:account")
    return render(request, "store/register.html", {"form": form})


@login_required
def account(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/account.html", {"orders": orders})


@require_POST
def sign_out(request):
    logout(request)
    messages.success(request, "Güvenle çıkış yaptınız.")
    return redirect("store:index")


class StockError(Exception):
    pass


@login_required
def checkout(request):
    if "checkout_token" not in request.session:
        request.session["checkout_token"] = str(uuid.uuid4())
    form = CheckoutForm(request.POST or None, initial={"token": request.session["checkout_token"]})
    if request.method == "POST" and form.is_valid():
        token = form.cleaned_data["token"]
        existing = Order.objects.filter(token=token, user=request.user).first()
        if existing:
            return redirect("store:order_detail", order_id=existing.pk)
        if str(token) != request.session["checkout_token"]:
            form.add_error(None, "Bu formun süresi doldu. Sayfayı yenileyin.")
        else:
            try:
                with transaction.atomic():
                    cart = request.session.get("cart", {})
                    if not cart:
                        raise StockError("Sepetiniz boş. Önce ürün ekleyin.")
                    products = list(Product.objects.select_for_update().filter(pk__in=cart))
                    if len(products) != len(cart):
                        raise StockError("Sepetinizde artık bulunmayan ürün var. Sepetinizi düzenleyin.")
                    total = sum((p.price * cart[str(p.pk)] for p in products), Decimal("0.00"))
                    order = Order.objects.create(user=request.user, token=token, total=total,
                        full_name=form.cleaned_data["full_name"], address=form.cleaned_data["address"])
                    sizes = request.session.get("cart_sizes", {})
                    for product in products:
                        quantity = cart[str(product.pk)]
                        changed = Product.objects.filter(pk=product.pk, is_active=True, stock__gte=quantity).update(stock=F("stock") - quantity)
                        if quantity < 1 or not changed:
                            raise StockError(f"{product.name} için yeterli stok yok. Sepetinizi güncelleyin.")
                        OrderItem.objects.create(order=order, product=product, name=product.name,
                            price=product.price, quantity=quantity, size=sizes.get(str(product.pk), ""))
                request.session["checkout_token"] = str(uuid.uuid4())
                request.session["cart"] = {}
                request.session["cart_sizes"] = {}
                return redirect("store:order_detail", order_id=order.pk)
            except IntegrityError:
                existing = Order.objects.filter(token=token, user=request.user).first()
                if existing:
                    return redirect("store:order_detail", order_id=existing.pk)
                form.add_error(None, "İşlem tamamlanamadı. Lütfen yeniden deneyin.")
            except StockError as error:
                form.add_error(None, str(error))
    return render(request, "store/checkout.html", {"form": form})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})
