from django.db import models
from articles.models import Article

class Location(models.Model):
    name = models.CharField("IG Location Name", max_length=100, blank=True, null=True)
    location_id = models.CharField("IG Location ID", max_length=200, blank=True, null=True, default=None)
    latitude = models.CharField("IG Location LAT", max_length=100, blank=True, null=True)
    longitude = models.CharField("IG Location LNG", max_length=100, blank=True, null=True)
    subscription_id = models.CharField("IG subscription ID", max_length=100, blank=True, null=True)
    articles = models.ManyToManyField(Article, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    class Meta:
        verbose_name = 'Instagram Location'
        verbose_name_plural = 'Instagram Locations'
        ordering = ['-timestamp',]

    def __unicode__(self):
        return self.name
        
    def shown_in_articles(self):
        return "\n".join([p.title for p in self.articles.all()])
        

class BadPerson(models.Model):
    username = models.CharField("IG username", max_length=100, blank=True, null=True)
    user_id = models.CharField("IG user ID", max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    
    class Meta:
        verbose_name = 'Bad Instagrammer'
        verbose_name_plural = 'Bad People'
        ordering = ['-timestamp',]

    def __unicode__(self):
        return self.username


class IGTag(models.Model):
    tag = models.CharField("IG tag", max_length=200, blank=True)
    ig_id = models.CharField("IG ID", max_length=200, blank=True, null=True, default=None)
    location = models.ForeignKey(Location, blank=True, null=True)
    articles = models.ManyToManyField(Article, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Instagram Tag'
        verbose_name_plural = 'Instagram Tags'
        ordering = ['-timestamp',]

    def __unicode__(self):
        return self.tag

    def shown_in_articles(self):
        return "\n".join([p.title for p in self.articles.all()])

# Create your models here.
class InstaPost(models.Model):
    insta_id = models.CharField("IG id", max_length=200, blank=True)
    username = models.CharField("IG username", max_length=100, blank=True)
    link = models.URLField("Link to IG post", max_length=100, blank=True)
    profile_picture = models.URLField("Profile Pic URL", max_length=500, blank=True)
    thumbnail = models.CharField("thumbnail URL", max_length=200, blank=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    #tag = models.CharField("IG tag", max_length=200, blank=True)
    tag = models.ForeignKey(IGTag, null=True, blank=True)
    standard_resolution = models.CharField("image URL", max_length=200, blank=True)
    caption_text = models.TextField("Caption", blank=True)
    created_time =  models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Instagram Post'
        verbose_name_plural = 'Instagram Posts'
        ordering = ['-created_time', ]

    def __unicode__(self):
        return self.insta_id