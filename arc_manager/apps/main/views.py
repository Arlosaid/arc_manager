from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.plans.models import Plan, Subscription, UpgradeRequest
from apps.orgs.models import Organization

User = get_user_model()

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    """Vista del dashboard principal con métricas reales"""
    current_user = request.user
    
    # Obtener fechas para filtros
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Métricas generales del sistema
    total_users = User.objects.count()
    total_organizations = Organization.objects.count()
    total_plans = Plan.objects.filter(is_active=True).count()
    total_subscriptions = Subscription.objects.filter(status='active').count()
    
    # Métricas de crecimiento
    new_users_this_month = User.objects.filter(date_joined__gte=this_month).count()
    new_users_last_month = User.objects.filter(
        date_joined__gte=last_month,
        date_joined__lt=this_month
    ).count()
    
    new_orgs_this_month = Organization.objects.filter(created_at__gte=this_month).count()
    new_orgs_last_month = Organization.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    
    # Calcular porcentajes de crecimiento
    def calculate_growth_percentage(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)
    
    user_growth = calculate_growth_percentage(new_users_this_month, new_users_last_month)
    org_growth = calculate_growth_percentage(new_orgs_this_month, new_orgs_last_month)
    
    # Obtener la organización del usuario actual
    user_organization = current_user.organization if hasattr(current_user, 'organization') else None
    
    # Métricas de planes
    plan_stats = Plan.objects.filter(is_active=True).annotate(
        subscription_count=Count('subscription', filter=Q(subscription__status='active'))
    ).order_by('-subscription_count')
    
    # Actividad reciente
    recent_activities = []
    
    # Usuarios recientes (filtrados por organización)
    try:
        if user_organization:
            recent_users = User.objects.filter(organization=user_organization).order_by('-date_joined')[:5]
            for user_obj in recent_users:
                recent_activities.append({
                    'type': 'user_created',
                    'title': f'Nuevo usuario: {user_obj.first_name} {user_obj.last_name}',
                    'description': f'Usuario {user_obj.email} se registró en tu organización',
                    'time': user_obj.date_joined,
                    'icon': 'fas fa-user-plus',
                    'color': 'success'
                })
    except Exception as e:
        pass  # Ignorar errores en usuarios recientes
    
    # Organizaciones recientes (esto puede ser una actividad global o la propia)
    try:
        if user_organization:
            recent_orgs = Organization.objects.filter(id=user_organization.id).order_by('-created_at')[:1]
            for org in recent_orgs:
                recent_activities.append({
                    'type': 'org_created',
                    'title': f'Se creó tu organización: {org.name}',
                    'description': f'La organización {org.name} fue registrada',
                    'time': org.created_at,
                    'icon': 'fas fa-building',
                    'color': 'primary'
                })
    except Exception as e:
        pass  # Ignorar errores en organizaciones recientes
    
    # Solicitudes de actualización recientes (filtradas por organización)
    try:
        if user_organization:
            upgrade_requests = UpgradeRequest.objects.filter(
                requested_by__organization=user_organization
            ).select_related('requested_by').order_by('-requested_date')[:3]
            for upgrade_request in upgrade_requests:
                recent_activities.append({
                    'type': 'upgrade_request',
                    'title': f'Solicitud de actualización',
                    'description': f'Usuario {upgrade_request.requested_by.email} solicita actualización',
                    'time': upgrade_request.requested_date,
                    'icon': 'fas fa-arrow-up',
                    'color': 'warning'
                })
    except Exception as e:
        pass  # Ignorar errores en solicitudes de upgrade
    
    # Ordenar actividades por fecha
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]
    
    # Datos para gráficos
    chart_data = {
        'users_monthly': [],
        'orgs_monthly': [],
        'revenue_monthly': []
    }
    
    # Datos de los últimos 6 meses
    try:
        for i in range(6):
            month_date = today.replace(day=1) - timedelta(days=i*30)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            users_count = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lte=month_end
            ).count()
            
            orgs_count = Organization.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            chart_data['users_monthly'].insert(0, {
                'month': month_start.strftime('%b'),
                'value': users_count
            })
            
            chart_data['orgs_monthly'].insert(0, {
                'month': month_start.strftime('%b'),
                'value': orgs_count
            })
    except Exception as e:
        # Si hay error en los datos del gráfico, usar datos vacíos
        chart_data = {
            'users_monthly': [],
            'orgs_monthly': [],
            'revenue_monthly': []
        }
    
    # Contar solicitudes pendientes
    try:
        pending_upgrades = UpgradeRequest.objects.filter(status='pending').count()
    except Exception as e:
        pending_upgrades = 0
    
    # Determinar nombre a mostrar
    greeting_name = current_user.get_full_name().strip() if hasattr(current_user, 'get_full_name') else ''
    if not greeting_name:
        greeting_name = current_user.username or getattr(current_user, 'email', '') or 'Usuario'

    context = {
        'user': current_user,
        'greeting_name': greeting_name,
        'organization': user_organization,
        
        # Métricas principales
        'total_users': total_users,
        'total_organizations': total_organizations,
        'total_plans': total_plans,
        'total_subscriptions': total_subscriptions,
        
        # Métricas de crecimiento
        'new_users_this_month': new_users_this_month,
        'new_orgs_this_month': new_orgs_this_month,
        'user_growth': user_growth,
        'org_growth': org_growth,
        
        # Estadísticas de planes
        'plan_stats': plan_stats,
        
        # Actividades recientes
        'recent_activities': recent_activities,
        
        # Datos para gráficos
        'chart_data': chart_data,
        
        # Métricas adicionales
        'active_subscriptions': total_subscriptions,
        'subscription_rate': round((total_subscriptions / total_users * 100), 1) if total_users > 0 else 0,
        'pending_upgrades': pending_upgrades,
        'tasks': [],  # Placeholder hasta que se implemente módulo de tareas
    }
    
    return render(request, 'dashboard.html', context)