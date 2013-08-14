# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PlaceStickers'
        db.create_table(u'stig_placestickers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Place'])),
            ('sticker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Sticker'])),
            ('modifier', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'stig', ['PlaceStickers'])


    def backwards(self, orm):
        # Deleting model 'PlaceStickers'
        db.delete_table(u'stig_placestickers')


    models = {
        u'stig.comment': {
            'Meta': {'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Comment']", 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Place']"}),
            'stickers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['stig.Sticker']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.StigUser']"})
        },
        u'stig.place': {
            'Meta': {'object_name': 'Place'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'geolocation': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'stig.placestickers': {
            'Meta': {'object_name': 'PlaceStickers'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.IntegerField', [], {}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Place']"}),
            'sticker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Sticker']"})
        },
        u'stig.sticker': {
            'Meta': {'object_name': 'Sticker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'stig.stiguser': {
            'Meta': {'object_name': 'StigUser'},
            'avatar': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['stig']