# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Advert'
        db.create_table(u'sponsors_advert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('adimg', self.gf('filebrowser.fields.FileBrowseField')(max_length=200, null=True, blank=True)),
            ('adlink', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('position', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 6, 3, 0, 0))),
        ))
        db.send_create_signal(u'sponsors', ['Advert'])


    def backwards(self, orm):
        # Deleting model 'Advert'
        db.delete_table(u'sponsors_advert')


    models = {
        u'sponsors.advert': {
            'Meta': {'ordering': "['-add_date']", 'object_name': 'Advert'},
            'add_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 6, 3, 0, 0)'}),
            'adimg': ('filebrowser.fields.FileBrowseField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'adlink': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'position': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['sponsors']