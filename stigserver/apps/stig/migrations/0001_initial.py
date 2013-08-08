# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StigUser'
        db.create_table(u'stig_stiguser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('avatar', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('fb_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'stig', ['StigUser'])

        # Adding model 'Place'
        db.create_table(u'stig_place', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('image', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'stig', ['Place'])

        # Adding model 'Sticker'
        db.create_table(u'stig_sticker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('image', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'stig', ['Sticker'])

        # Adding model 'Comment'
        db.create_table(u'stig_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Place'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.StigUser'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stig.Comment'])),
        ))
        db.send_create_signal(u'stig', ['Comment'])

        # Adding M2M table for field stickers on 'Comment'
        m2m_table_name = db.shorten_name(u'stig_comment_stickers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('comment', models.ForeignKey(orm[u'stig.comment'], null=False)),
            ('sticker', models.ForeignKey(orm[u'stig.sticker'], null=False))
        ))
        db.create_unique(m2m_table_name, ['comment_id', 'sticker_id'])


    def backwards(self, orm):
        # Deleting model 'StigUser'
        db.delete_table(u'stig_stiguser')

        # Deleting model 'Place'
        db.delete_table(u'stig_place')

        # Deleting model 'Sticker'
        db.delete_table(u'stig_sticker')

        # Deleting model 'Comment'
        db.delete_table(u'stig_comment')

        # Removing M2M table for field stickers on 'Comment'
        db.delete_table(db.shorten_name(u'stig_comment_stickers'))


    models = {
        u'stig.comment': {
            'Meta': {'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Comment']"}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.Place']"}),
            'stickers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['stig.Sticker']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stig.StigUser']"})
        },
        u'stig.place': {
            'Meta': {'object_name': 'Place'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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