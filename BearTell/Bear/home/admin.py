from django.contrib import admin
from .models import category_parent,category_child,analyze_type,sensor_name,data_source

class child_admin(admin.ModelAdmin):
    list_display = ['name','publishing_date']
    class Meta:
        model = category_parent

admin.site.register(category_parent)
admin.site.register(category_child)
admin.site.register(analyze_type)
admin.site.register(sensor_name)
admin.site.register(data_source)



