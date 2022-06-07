import django_filters
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from faq.models import Faq


class FaqNode(DjangoObjectType):
    class Meta:
        model = Faq
        interfaces = (relay.Node,)


class FaqFilterSet(django_filters.FilterSet):
    @property
    def qs(self):
        return super().qs.order_by('order')

    class Meta:
        model = Faq
        fields = ('id',)


class Query(object):
    faq = DjangoFilterConnectionField(FaqNode, filterset_class=FaqFilterSet)
