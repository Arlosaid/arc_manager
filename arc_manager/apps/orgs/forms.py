from django import forms
from .models import Organization
from apps.plans.models import Plan

class OrganizationForm(forms.ModelForm):
    """Formulario para crear y editar organizaciones"""
    
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'description', 'plan', 'is_active']
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
            'plan': forms.Select(attrs={
                'class': 'form-control',
                'data-toggle': 'tooltip',
                'title': 'El plan determina automáticamente el límite de usuarios y características disponibles'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar planes activos
        self.fields['plan'].queryset = Plan.objects.filter(is_active=True).order_by('price', 'max_users')
        # Hacer que el plan sea obligatorio
        self.fields['plan'].required = True
        self.fields['plan'].empty_label = None  # No permitir opción vacía
        
        # Si es una nueva organización, establecer plan gratuito por defecto
        if not self.instance.pk:
            try:
                plan_gratuito = Plan.objects.get(name='gratuito')
                self.fields['plan'].initial = plan_gratuito.pk
                # Agregar texto de ayuda específico para nueva organización
                self.fields['plan'].help_text = "El plan seleccionado determinará automáticamente el número máximo de usuarios permitidos. Puedes cambiar el plan más tarde."
            except Plan.DoesNotExist:
                self.fields['plan'].help_text = "Selecciona un plan para determinar los límites y características de la organización."
        else:
            self.fields['plan'].help_text = "Cambiar el plan modificará automáticamente los límites de usuarios y características disponibles."
    
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
    
    def clean_plan(self):
        plan = self.cleaned_data.get('plan')
        if not plan:
            raise forms.ValidationError("Debes seleccionar un plan.")
        
        # Si estamos editando una organización, verificar que el nuevo plan permita los usuarios actuales
        if self.instance.pk:
            current_user_count = self.instance.get_user_count()
            if current_user_count > plan.max_users:
                raise forms.ValidationError(
                    f"No puedes cambiar a este plan porque tu organización tiene {current_user_count} usuarios "
                    f"y el plan seleccionado solo permite {plan.max_users}. "
                    f"Reduce el número de usuarios primero o selecciona un plan con mayor capacidad."
                )
        
        return plan
    
    def save(self, commit=True):
        """Sobrescribir save para asegurar que el plan se asigne correctamente"""
        instance = super().save(commit=False)
        
        # Asegurar que el plan esté asignado
        if not instance.plan and self.cleaned_data.get('plan'):
            instance.plan = self.cleaned_data['plan']
        
        if commit:
            instance.save()
        return instance 