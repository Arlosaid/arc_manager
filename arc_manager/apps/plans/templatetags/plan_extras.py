from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def subtract(value, arg):
    """Sustrae el argumento del valor."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide el valor por el argumento."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calcula el porcentaje de value respecto a total."""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def format_currency(value):
    """Formatea un número como moneda mexicana."""
    try:
        return f"${float(value):,.0f}"
    except (ValueError, TypeError):
        return "$0"

@register.filter
def days_to_percentage(days, total_days=30):
    """Convierte días restantes a porcentaje para progress bars."""
    try:
        if float(total_days) == 0:
            return 0
        remaining_percentage = (float(days) / float(total_days)) * 100
        return min(max(remaining_percentage, 0), 100)
    except (ValueError, TypeError):
        return 0

@register.filter
def usage_status_class(percentage):
    """Retorna la clase CSS apropiada según el porcentaje de uso."""
    try:
        pct = float(percentage)
        if pct >= 90:
            return 'danger'
        elif pct >= 70:
            return 'warning'
        else:
            return 'safe'
    except (ValueError, TypeError):
        return 'safe'

@register.filter
def mul(value, arg):
    """Alias para multiply - multiplica el valor por el argumento."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Alias para divide - divide el valor por el argumento."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def plan_savings(new_price, current_price, months=12):
    """Calcula el ahorro anual potencial."""
    try:
        monthly_difference = float(new_price) - float(current_price)
        return monthly_difference * float(months)
    except (ValueError, TypeError):
        return 0 