# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Popular_video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('up_rate', models.IntegerField(default=0)),
                ('status', models.CharField(default=b'A', max_length=45, choices=[('A', 'Active'), ('D', 'Deleted'), ('B', 'Building')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Server_status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_status', models.CharField(default=b'S', max_length=45, choices=[('R', 'Running'), ('W', 'Waiting'), ('S', 'Stopped')])),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('stop_time', models.DateTimeField(blank=True)),
                ('run_time', models.IntegerField(default=0)),
                ('status', models.CharField(default=b'A', max_length=45, choices=[('A', 'Active'), ('D', 'Deleted'), ('B', 'Building')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sites',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('ch_name', models.CharField(default=b'None', max_length=200)),
                ('status', models.CharField(default=b'A', max_length=45, choices=[('A', 'Active'), ('D', 'Deleted'), ('B', 'Building')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Snapshots',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.FilePathField(max_length=200)),
                ('get_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'A', max_length=45, choices=[('A', 'Active'), ('D', 'Deleted'), ('B', 'Building')])),
                ('site', models.ForeignKey(to='spider.Sites')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(max_length=500)),
                ('playcount', models.IntegerField(default=0)),
                ('thumbnail', models.FilePathField(max_length=200)),
                ('crawling_time', models.DateTimeField(auto_now_add=True)),
                ('favorite', models.IntegerField(default=0)),
                ('community', models.IntegerField(default=0)),
                ('upcount', models.IntegerField(default=0)),
                ('downcount', models.IntegerField(default=0)),
                ('url', models.URLField()),
                ('status', models.CharField(default=b'B', max_length=45, choices=[('A', 'Active'), ('D', 'Deleted'), ('B', 'Building')])),
                ('site', models.ForeignKey(to='spider.Sites')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
