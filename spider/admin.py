from django.contrib import admin

# Register your models here.
from spider.models import Videos, Popular_video, Sites


@admin.register(Videos, Popular_video, Sites)
class AuthorAdmin(admin.ModelAdmin):
    pass
# admin.site.register(Videos, AuthorAdmin)