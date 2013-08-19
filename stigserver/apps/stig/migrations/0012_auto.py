# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field friends on 'StigUser'
        m2m_table_name = db.shorten_name(u'stig_stiguser_friends')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_stiguser', models.ForeignKey(orm[u'stig.stiguser'], null=False)),
            ('to_stiguser', models.ForeignKey(orm[u'stig.stiguser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_stiguser_id', 'to_stiguser_id'])


    def backwards(self, orm):
        # Removing M2M table for field friends on 'StigUser'
        db.delete_table(db.shorten_name(u'stig_stiguser_friends'))


    models = {
        u'stig.checkin': {
            'Meta': {'object_name': 'Checkin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Place']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.StigUser']"})
        },
        u'stig.comment': {
            'Meta': {'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Comment']", 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Place']"}),
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
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Comment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.IntegerField', [], {}),
            'sticker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Sticker']"})
        },
        u'stig.sticker': {
            'Meta': {'object_name': 'Sticker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'stig.stiguser': {
            'Meta': {'object_name': 'StigUser'},
            'avatar': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'fb_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'friends_rel_+'", 'to': u"orm['stig.StigUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['stig']