from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def project_file_path(instance, filename):
    """
    Generate the file path for a new project file.
    Example: project_1/Permits/document.pdf
    """
    return f'project_{instance.project.id}/{instance.upload_phase}/{filename}'

class Project(models.Model):
    """Represents an architectural project."""

    class Phases(models.TextChoices):
        PRELIMINARY = 'Preliminary', _('Preliminary Design')
        EXECUTIVE = 'Executive', _('Executive Project')
        PERMITS = 'Permits', _('Permits & Licensing')
        CONSTRUCTION = 'Construction', _('Construction')
        DELIVERY = 'Delivery', _('Final Delivery')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_("Owner")
    )
    name = models.CharField(_("Project Name"), max_length=255)
    client = models.CharField(_("Client Name"), max_length=255, blank=True)
    phase = models.CharField(
        _("Current Phase"),
        max_length=50,
        choices=Phases.choices,
        default=Phases.PRELIMINARY
    )
    created_at = models.DateTimeField(_("Creation Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Task(models.Model):
    """Represents a specific task within a project."""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_("Project")
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name=_("Assigned To")
    )
    title = models.CharField(_("Task Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    completed = models.BooleanField(_("Completed?"), default=False)
    created_at = models.DateTimeField(_("Creation Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ['created_at']

    def __str__(self):
        return self.title

class ProjectFile(models.Model):
    """Represents a file associated with a project."""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_("Project")
    )
    upload_phase = models.CharField(
        _("Phase when uploaded"),
        max_length=50,
        choices=Project.Phases.choices
    )
    file = models.FileField(
        _("File"),
        upload_to=project_file_path
    )
    uploaded_at = models.DateTimeField(_("Upload Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("Project File")
        verbose_name_plural = _("Project Files")
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file.name
