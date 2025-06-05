from django import forms
from .models import Organization
from apps.plans.models import Plan

class OrganizationForm(forms.ModelForm):
    """Formulario para crear y editar organizaciones"""
    
    # Campo adicional para seleccionar el plan inicial
    initial_plan = forms.ModelChoiceField(
        queryset=Plan.objects.filter(is_active=True).order_by('price', 'max_users'),
        required=True,
        empty_label=None,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-toggle': 'tooltip',
            'title': 'El plan determina automáticamente el límite de usuarios y características disponibles'
        }),
        help_text="Selecciona el plan inicial para la organización. Se creará automáticamente una suscripción."
    )
    
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'description', 'is_active']
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
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es una nueva organización, establecer plan de prueba por defecto
        if not self.instance.pk:
            try:
                trial_plan = Plan.objects.get(name='trial', is_active=True)
                self.fields['initial_plan'].initial = trial_plan.pk
                self.fields['initial_plan'].help_text = "Se creará automáticamente una suscripción de prueba gratuita de 30 días."
            except Plan.DoesNotExist:
                try:
                    basic_plan = Plan.objects.get(name='basic', is_active=True)
                    self.fields['initial_plan'].initial = basic_plan.pk
                except Plan.DoesNotExist:
                    pass
        else:
            # Si es edición, no mostrar el campo de plan inicial
            if 'initial_plan' in self.fields:
                del self.fields['initial_plan']
    
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
    
    def clean_initial_plan(self):
        # Solo validar si es una nueva organización
        if not self.instance.pk:
            plan = self.cleaned_data.get('initial_plan')
            if not plan:
                raise forms.ValidationError("Debes seleccionar un plan inicial.")
            return plan
        return None
    
    def save(self, commit=True):
        """Sobrescribir save para crear la suscripción automáticamente"""
        from apps.plans.models import Subscription
        
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Si es una nueva organización, crear la suscripción
            if not hasattr(instance, 'subscription'):
                initial_plan = self.cleaned_data.get('initial_plan')
                if initial_plan:
                    Subscription.objects.create(
                        organization=instance,
                        plan=initial_plan
                    )
        
        return instance 