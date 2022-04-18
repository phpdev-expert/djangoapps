from django import forms
from ais.models import Ais, AisSettings
class AisForm(forms.ModelForm):
    class Meta:
        model = Ais
        fields = "__all__"

class AisSettingForm(forms.ModelForm):
    class Meta:
        model = AisSettings
        fields = "__all__"
