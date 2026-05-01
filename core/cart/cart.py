# cart/cart.py
from decimal import Decimal
from django.conf import settings
from restaurants.models import MenuItem

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Initialize an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, item, quantity=1):
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(item.price)}
        
        self.cart[item_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Mark the session as "modified" to ensure it gets saved
        self.session.modified = True

    def __iter__(self):
        item_ids = self.cart.keys()
        items = MenuItem.objects.filter(id__in=item_ids)
        cart = self.cart.copy()
        for item in items:
            cart[str(item.id)]['item'] = item

        for item in cart.values():
            item['total_price'] = Decimal(item['price']) * item['quantity']
            yield item

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    # cart/cart.py (Add these methods to your existing Cart class) 
    def remove(self, item):
        item_id = str(item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    # def clear(self):
    #     # Empty the cart session completely
    #     del self.session['cart']
    #     self.save()
        
    # cart/cart.py (Add this to your Cart class)

    def decrement(self, item):
        item_id = str(item.id)
        if item_id in self.cart:
            self.cart[item_id]['quantity'] -= 1
            # If quantity reaches 0, remove the item entirely
            if self.cart[item_id]['quantity'] <= 0:
                self.remove(item)
            self.save()

    def clear(self):
        # Remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()



