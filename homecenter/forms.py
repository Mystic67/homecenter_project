from django.forms import ModelForm
from .models import Instances


class InstanceForm(ModelForm):
    class Meta:
        model = Instances
        fields = ['name', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({'id': 'input_name',
                                                 'class': 'input_name form-control rounded',
                                                 'placeholder': "Porte fenêtre"})

        self.fields['location'].widget.attrs.update({'id': 'input_location',
                                                     'class': 'input_location form-control rounded',
                                                     'placeholder': "Salon"})

