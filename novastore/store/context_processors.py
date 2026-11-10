def cart_summary(request):
    cart = request.session.get("cart", {})
    return {"cart_quantity": sum(cart.values()), "cart_product_count": len(cart)}
