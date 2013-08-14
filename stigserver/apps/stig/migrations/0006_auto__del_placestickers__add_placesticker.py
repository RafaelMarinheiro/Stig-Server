# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'PlaceStickers'
        db.delete_table(u'stig_placestickers')

        # Adding model 'PlaceSticker'
        db.create_table(u'stig_placesticker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Place'])),
            ('sticker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Sticker'])),
            ('modifier', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'stig', ['PlaceSticker'])


    def backwards(self, orm):
        # Adding model 'PlaceStickers'
        db.create_table(u'stig_placestickers', (
            ('modifier', self.gf('django.db.models.fields.IntegerField')()),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Place'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sticker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Sticker'])),
        ))
        db.send_create_signal(u'stig', ['PlaceStickers'])

        # Deleting model 'PlaceSticker'
        db.delete_table(u'stig_placesticker')


    models = {
        u'stig.comment': {
            'Meta': {'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Comment']", 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Place']"}),
            'sticker_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['stig.PlaceSticker']", 'symmetrical': 'False'}),
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
        u'stig.placesticker': {
            'Meta': {'object_name': 'PlaceSticker'},
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