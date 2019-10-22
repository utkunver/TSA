from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from .models import category_parent, category_child, analyze_type,sensor_name,data_source
from .serializers import CategorySerializer, SubCategorySerializer, AnalyzeTypeSerializer,DataSourceSerializer
import requests

class Rest(APIView):
    def home(request):
        query = request.GET.get('metric')


class Categories(APIView):
    def get(self, request):
        response = category_parent.objects.all()
        serializer = CategorySerializer(response, many=True)
        return Response(serializer.data)
    def post(self, request):
        pass

class SubCategories(APIView):
    def get(self, request):
        parent_id = self.request.query_params.get('parent_id')
        response = category_child.objects.filter(parent_id=parent_id)
        serializer = SubCategorySerializer(response, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass

class SensorName(APIView):
    def get(self, request):
        child_id = self.request.query_params.get('child_id')
        ds_id = self.request.query_params.get('ds_id')
        response1 = sensor_name.objects.filter(child_id=child_id,ds_id=ds_id)
        response2 = data_source.objects.filter(id=ds_id)
        if response1.count()>0 and response2.count()>0:
            url = response2.first().ip+'/suggest?type=metrics&max=1000000&q='+response1.first().key_word
            r = requests.get(url)
            if r is not None:
                newData = []
                counter = 0
                for item in r.json():
                    newData.append({"id": counter, "sensor_name": item})
                    counter += 1
                return Response(newData)

        return Response("")
    def post(self, request):
        pass

class AnalizButton(APIView):
    def get(self, request):
        dataSourceType = self.request.query_params.get('dataSourceType')
        startDate = self.request.query_params.get('startDate')
        endDate= self.request.query_params.get('endDate')
        sensorName = self.request.query_params.get('sensorName')
        analysisType = self.request.query_params.get('analysisType')
        zamanDilimi = self.request.query_params.get('zaman_dilimi')
        textZaman = self.request.query_params.get(('text_zaman'))
        anomali =  self.request.query_params.get('anomali')
        responses = str((data_source.objects.filter(id=dataSourceType).first()).ip)

        request_url = "http://localhost:5000/v1/"
        request_url += "?dataSourceType=" + responses
        request_url += "&startDate=" + startDate
        request_url += "&endDate=" + endDate
        request_url += "&sensorName=" + sensorName
        request_url += "&analysisType=" + analysisType
        request_url += "&zamanDilimi=" + zamanDilimi
        request_url += "&textZaman=" + textZaman
        request_url += "&anomali=" + anomali
        response = requests.get(request_url)
# http://127.0.0.1:8000/api/?dataSourceType=1&startDate=2015/12/15-12:24:45&endDate=2016/01/09-12:24:45&sensorName=izmit.raw.9G2_X2_S2_EX_VFLD&analysisType=Arima&zaman_dilimi=m&text_zaman=10&anomali=1

class AnalyzeTypes(APIView):
    def get(self, request):
        response = analyze_type.objects.all()
        serializer = AnalyzeTypeSerializer(response, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass
class DataSource(APIView):
    def get(self, request):
        response = data_source.objects.all()
        serializer = DataSourceSerializer(response, many=True)
        return Response(serializer.data)

    def post(self, request):
        pass

class HomePageView(TemplateView):
    template_name = 'home.html'
