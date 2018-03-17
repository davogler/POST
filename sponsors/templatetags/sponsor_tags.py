from django.template import Library
from django import template
from django.db.models import get_model


from sponsors.models import Advert
     
register = Library()
register = template.Library()


def adblock(request, position):
    ads = Advert.objects.filter(position=position).filter(is_active=True)
    return {'ads': ads}
    
register.inclusion_tag('sponsors/adblock.html')(adblock)