
from django.contrib import admin
from django.urls import  path
from django.conf.urls import url
from home.views import HomePageView
from rest_framework.urlpatterns import format_suffix_patterns
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    url(r'^categories/', views.Categories.as_view()),
    url(r'^sub_categories/', views.SubCategories.as_view()),
    url(r'^analyzers/', views.AnalyzeTypes.as_view()),
    url(r'^sensor_name/', views.SensorName.as_view()),
    url(r'^data_source', views.DataSource.as_view()),
    url(r'^analiz_baslat', views.AnalizButton.as_view()),
    url(r'^api/', views.AnalizButton.as_view()),

]
urlpatterns = format_suffix_patterns(urlpatterns)
