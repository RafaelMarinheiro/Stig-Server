# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Contact.timestamp'
        db.alter_column(u'frontend_contact', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))
        # Adding unique constraint on 'Contact', fields ['email']
        db.create_unique(u'frontend_contact', ['email'])


    def backwards(self, orm):
        # Removing unique constraint on 'Contact', fields ['email']
        db.delete_unique(u'frontend_contact', ['email'])


        # Changing field 'Contact.timestamp'
        db.alter_column(u'frontend_contact', 'timestamp', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        u'frontend.contact': {
            'Meta': {'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['frontend']