import random

import django_filters
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from rest_framework.relations import PrimaryKeyRelatedField

from internships.models import Company, InternshipOffer, CompanyContact, InternshipTag


class InternshipNode(DjangoObjectType):
    class Meta:
        model = InternshipOffer
        interfaces = (relay.Node,)
        exclude_fields = ('applicants',)



class InternshipTagNode(DjangoObjectType):
    class Meta:
        model = InternshipTag
        interfaces = (relay.Node,)


class CompanyContactNode(DjangoObjectType):
    class Meta:
        model = CompanyContact
        interfaces = (relay.Node,)
        exclude = []


class InternshipFilterSet(django_filters.FilterSet):
    class Meta:
        model = InternshipOffer
        fields = ['is_paid']


class ImageKitSpec(graphene.ObjectType):
    width = graphene.Int(required=True, description="Image width in pixels.")
    url = graphene.String(required=True, description="Absolute url path to image file.")


class CompanyNode(DjangoObjectType):
    internships = DjangoFilterConnectionField(InternshipNode, filterset_class=InternshipFilterSet)
    total_capacity = graphene.Int(source='total_capacity', required=True)
    num_internships = graphene.Int(source='num_internships', required=True)
    exclude_fields = ('group','visible_for_students')
    contacts = PrimaryKeyRelatedField(queryset=CompanyContact.objects, required=False)

    logo = graphene.List(graphene.NonNull(ImageKitSpec), required=True,
                         description="A list of sizes available for the logo image. "
                                     "The list is sorted in descending order of image width.")

    def resolve_logo(self, info):
        company = self  # type: Company
        return [ImageKitSpec(**sz) for sz in company.logo_sizes]

    class Meta:
        model = Company
        interfaces = (relay.Node,)


class CompanyFilterSet(django_filters.FilterSet):
    has_internships = django_filters.BooleanFilter(method='_has_internships')

    @property
    def qs(self):
        result = list(super().qs.filter(visible_for_students=True))
        random.shuffle(result)
        return result

    class Meta:
        model = Company
        fields = ['has_internships']

    def _has_internships(self, queryset, name, value):
        assert name == "has_internships"
        filter_args = {'num_internships__gt': 0} if value else {}

        return queryset \
            .filter(visible_for_students=True,**filter_args)


class Query(object):
    company = relay.Node.Field(CompanyNode)
    company_by_slug = graphene.Field(CompanyNode, slug=graphene.String(required=True))
    internship = relay.Node.Field(InternshipNode)

    companies = DjangoFilterConnectionField(CompanyNode, filterset_class=CompanyFilterSet)

    def resolve_company_by_slug(self, info, *, slug):
        try:
            return Company.objects.get(slug=slug,visible_for_students=True)
        except Company.DoesNotExist:
            return None
