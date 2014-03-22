from django.db import models
import datetime
from django.utils.timezone import utc
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

class LiveEntryManager(models.Manager):
    def get_query_set(self):
        return super(LiveEntryManager, self).get_query_set().exclude(status=self.model.DRAFT_STATUS)
		
class PublishedEntryManager(models.Manager):
	def get_query_set(self):
		return super(PublishedEntryManager, self).get_query_set().exclude(status=self.model.DRAFT_STATUS)

class DraftEntryManager(models.Manager):
    def get_query_set(self):
        return super(DraftEntryManager, self).get_query_set().filter(status=self.model.DRAFT_STATUS)

class Article(models.Model):
    """Model to store Articles"""
    PUBLISHED_STATUS = 1
    DRAFT_STATUS = 2
    STATUS_CHOICES = (
        (PUBLISHED_STATUS, 'Published'),
        (DRAFT_STATUS, 'Draft'),
    )
    title = models.CharField(max_length=250)
    tagline = models.TextField(blank=True)
    intro = models.TextField(blank=True, help_text='For article list view teaser- can be identical to standfirst if desired.')
    standfirst = models.TextField(blank=True, help_text='First paragraph in article body.')
    body = models.TextField()

    slug = models.SlugField(unique_for_date='pub_date')
    hero = FileBrowseField("Hero Image", max_length=200, extensions=[".jpg",".png", ".gif"], blank=True, null=True, help_text='Choose an huge image for this article. Minimum 1280 x 900')
    hero_alt = FileBrowseField("Hero Alternate Image", max_length=200, extensions=[".jpg",".png", ".gif"], blank=True, null=True, help_text='For displaying in SM metadata when Hero Image just aint right for it. Optional.')
    hero_credit = models.CharField(max_length=250, blank=True)
    screen = models.BooleanField(default=False, help_text='check for dark image needing light screen in header')
    pub_date = models.DateTimeField(default=datetime.datetime.now, blank=True)
    author = models.ManyToManyField('Author', blank=True)
    photog = models.ManyToManyField('Photog', blank=True)
    illus = models.ManyToManyField('Illus', blank=True)
    sponsor = models.ForeignKey('Sponsor', blank=True, null=True)
    more_info = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    issue = models.ForeignKey('Issue', blank=True, null=True)
    special_js = models.TextField(blank=True)
    special_css = models.TextField(blank=True, null=True, help_text='Mainly h2.unique and p.tagline')
    template_name = models.CharField(max_length=250, blank=True, help_text='enter optional template to override default')
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT_STATUS)
    objects = models.Manager()	
    live = LiveEntryManager()
    draft = DraftEntryManager()
    published = PublishedEntryManager()
    
	
    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = "Articles"
        #app_label = "blog"
		
    def __unicode__(self):
        return self.title
		
    def save(self, force_insert=False, force_update=False):
        #self.body_html = markdown(self.body)
        #if self.excerpt:
        #	self.excerpt_html = markdown(self.excerpt)
        super(Article, self).save(force_insert, force_update)
        
    @models.permalink	
    def get_absolute_url(self):
        return ('article_detail', (), {'slug': self.slug })
        
	

class Image(models.Model):
    article = models.ForeignKey('Article')
    name = models.CharField(max_length=35)
    image = FileBrowseField("Inline IMage", max_length=200, extensions=[".jpg",".png", ".gif", ".svg"], blank=True, null=True, help_text='Inline image, yo. 960 640 or 525')
    caption = models.CharField(max_length=500, blank=True, null=True)

class Issue(models.Model):
    volume = models.CharField(max_length=250)
    month = models.CharField(max_length=250)
    cover_img = FileBrowseField("Cover Image", max_length=200, extensions=[".jpg",".png", ".gif"], blank=True, null=True, help_text='Upload a cover image; 1280px wide pls.')
    
    def thumb(self):
        return mark_safe(u'<img src="/media/%s" />' % (self.cover_img))
        thumb.short_description = 'Thumb'
        thumb.allow_tags = True
        
    class Meta:
        ordering = ['-month']
        verbose_name_plural = "Issues"
    	
    def __unicode__(self):
        return self.month
    
class Sponsor(models.Model):
    name = models.CharField(max_length=250)
    adimg = FileBrowseField("Ad Image", max_length=200, extensions=[".jpg",".png", ".gif"], blank=True, null=True, help_text='Upload an image to be used for advertising min width 525px')
    adlink = models.URLField()
    endorsement = models.TextField(blank=True) 
    add_date = models.DateTimeField(default=datetime.datetime.now())    
    
    class Meta:
        ordering = ['-add_date']
        verbose_name_plural = "Sponsors"
    	
    def __unicode__(self):
        return self.name  
        
class Author(models.Model):
    name = models.CharField(max_length=250)
    link = models.URLField(blank=True)
    colophon = models.TextField(blank=True) 
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Authors"
    	
    def __unicode__(self):
        return self.name
        
class Photog(models.Model):
    name = models.CharField(max_length=250)
    link = models.URLField(blank=True)
    colophon = models.TextField(blank=True) 
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Photographers"
    	
    def __unicode__(self):
        return self.name 
        
class Illus(models.Model):
    name = models.CharField(max_length=250)
    link = models.URLField(blank=True)
    colophon = models.TextField(blank=True) 
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Illustrators"
        	
    def __unicode__(self):
        return self.name        

	