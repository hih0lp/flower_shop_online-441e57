from decimal import Decimal
from django.conf import settings
from .models import Flower


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, flower, quantity=1):
        flower_id = str(flower.id)
        if flower_id not in self.cart:
            self.cart[flower_id] = {'quantity': 0, 'price': str(flower.price)}
        self.cart[flower_id]['quantity'] += quantity
        self.save()

    def update(self, flower, quantity):
        flower_id = str(flower.id)
        if flower_id in self.cart:
            self.cart[flower_id]['quantity'] = quantity
            if quantity <= 0:
                self.remove(flower)
            else:
                self.save()

    def remove(self, flower):
        flower_id = str(flower.id)
        if flower_id in self.cart:
            del self.cart[flower_id]
            self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def __iter__(self):
        flower_ids = self.cart.keys()
        flowers = Flower.objects.filter(id__in=flower_ids)
        cart = self.cart.copy()
        for flower in flowers:
            cart[str(flower.id)]['flower'] = flower
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
