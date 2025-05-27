from django import forms
from .models import Organization

class OrganizationForm(forms.ModelForm):
    """Formulario para crear y editar organizaciones"""
    
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'description', 'max_users', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la organización'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'identificador-unico'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional de la organización'
            }),
            'max_users': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            # Verificar que el slug sea único (excluyendo la instancia actual si es edición)
            qs = Organization.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este identificador ya está en uso.")
        return slug
    
    def clean_max_users(self):
        max_users = self.cleaned_data.get('max_users')
        if max_users and max_users < 1:
            raise forms.ValidationError("El número máximo de usuarios debe ser al menos 1.")
        return max_users 