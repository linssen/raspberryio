from django.db import models

from mezzanine.core.models import (Displayable, Ownable, Orderable, RichText,
    CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED)
from mezzanine.core.fields import RichTextField
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.timezone import now
from mezzanine.galleries.models import Gallery
from mezzanine.blog.models import BlogCategory


class Project(Displayable, Ownable, AdminThumbMixin):
    """
    A project submission
    """

    featured_photo = models.ImageField(
        upload_to='images/project_featured_photos', blank=True, null=True
    )
    featured_video = models.URLField(blank=True, default='')
    featured_video_thumbnail = models.ImageField(
        upload_to='images/project_featured_video_thumbnails',
        blank=True, null=True, editable=False
    )
    tldr = models.TextField('Summary',
        help_text='A brief summary of your project'
    )
    categories = models.ManyToManyField(BlogCategory, related_name='projects')
    score = models.IntegerField(default=0)
    created_datetime = models.DateTimeField('Created')
    modified_datetime = models.DateTimeField('Modified')

    admin_thumb_field = 'featured_photo'

    def save(self, *args, **kwargs):
        # Set project as draft by default
        if not self.id:
            self.status = CONTENT_STATUS_DRAFT
        # Set created and modified datetimes if not provided.
        if not self.id:
            self.created_datetime = now()
        self.modified_datetime = now()
        super(Project, self).save(*args, **kwargs)

    @property
    def is_published(self):
        return (self.publish_date <= now() and
            self.status == CONTENT_STATUS_PUBLISHED)

    @models.permalink
    def get_absolute_url(self):
        return ('project-detail', [self.slug])

    def __unicode__(self):
        return u'Project: {0}'.format(self.title)


class ProjectStep(Orderable, RichText):
    """
    A step in the process of creating the project
    """

    project = models.ForeignKey('Project', related_name='steps')
    gallery = models.OneToOneField(Gallery, blank=True, null=True)
    video = models.URLField(blank=True, default='')

    class Meta(object):
        order_with_respect_to = 'project'

    def is_editable(self, request):
        """
        Restrict in-line editing to the owner of the project and superusers.
        """
        user = request.user
        return user.is_superuser or user.id == self.project.user_id

    @property
    def order(self):
        """Exposes the step's _order attribute for use in templates"""
        return self._order

    @models.permalink
    def get_absolute_url(self):
        # FIXME: Change to project_step_detail when implemented
        return ('project-detail', [self.project.slug])

    def __unicode__(self):
        return u'ProjectStep: Step {0} of project {1}'.format(
            self._order, self.project.title
        )


class ProjectCategory(BlogCategory):
    class Meta(object):
        proxy = True