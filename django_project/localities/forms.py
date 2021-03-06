# -*- coding: utf-8 -*-
import logging
LOG = logging.getLogger(__name__)

import django.forms as forms

from .models import Domain
from .utils import render_fragment


class DomainModelForm(forms.ModelForm):
    """
    Used in django admin

    Special validation rules for template_fragment field
    """

    class Meta:
        model = Domain
        fields = ('name', 'description', 'template_fragment')

    def clean_template_fragment(self):
        try:
            render_fragment(self.cleaned_data['template_fragment'], {})
        except Exception, e:
            raise forms.ValidationError(
                'Template Syntax Error: {}'.format(e.message)
            )

        return self.cleaned_data['template_fragment']


class DomainForm(forms.Form):
    """
    Used when creating a new Locality

    Form will dynamically add every specification of an attribute as a simple
    CharField
    """

    lon = forms.FloatField()
    lat = forms.FloatField()

    def __init__(self, *args, **kwargs):
        # pop arguments which are not form fields
        domain = kwargs.pop('domain')

        super(DomainForm, self).__init__(*args, **kwargs)

        # populate form with attribute specifications
        for spec in domain.specification_set.select_related('attribute'):
            field = forms.CharField(
                label=spec.attribute.key, required=spec.required
            )
            self.fields[spec.attribute.key] = field


class LocalityForm(forms.Form):
    """
    Used when updating a Locality

    Form will dynamically add every specification of an attribute as a simple
    CharField, and prefill it with initial values
    """

    lon = forms.FloatField()
    lat = forms.FloatField()

    def __init__(self, *args, **kwargs):
        # pop arguments which are not form fields
        locality = kwargs.pop('locality')

        tmp_initial_data = {
            'lon': locality.geom.x, 'lat': locality.geom.y
        }

        # Locality forms are special as they automatically collect initial data
        # based on the actual models
        for value in locality.value_set.select_related('specification').all():
            tmp_initial_data.update({
                value.specification.attribute.key: value.data
            })

        # set initial form data
        kwargs.update({'initial': tmp_initial_data})

        super(LocalityForm, self).__init__(*args, **kwargs)

        for spec in (
                locality.domain.specification_set.select_related('attribute')):

            field = forms.CharField(
                label=spec.attribute.key, required=spec.required
            )
            self.fields[spec.attribute.key] = field
            self.fields[spec.attribute.key].widget.attrs.update(
                {'class': 'form-control'})
