from django.db import models
class category_parent(models.Model):
    name = models.CharField(max_length=255, verbose_name='Parent Categories')
    def __str__(self):
        return self.name

    class Meta:
        db_table = "category_parent"
class category_child(models.Model):
    name= models.CharField(max_length=255, verbose_name='Child Categories')
    parent_id = models.ForeignKey(category_parent, related_name="child", on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        db_table = "category_child"
class analyze_type(models.Model):
    name = models.CharField(max_length=255, verbose_name='Analyze name')
    module_name = models.CharField(max_length=255, verbose_name='Analyze module name')

    def __str__(self):
        return self.name
    class Meta:
        db_table = "analyze_type"
class data_source(models.Model):
    name = models.CharField(max_length=255, verbose_name='Data name')
    ip = models.CharField(max_length=255, verbose_name='ip')
    kimlik = models.CharField(max_length=255, verbose_name='Kimlik',null=True, blank= True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = "data_source"
class sensor_name(models.Model):
    key_word = models.CharField(max_length=255, verbose_name='key_word')
    child = models.ForeignKey(category_child, related_name="sensor", on_delete=models.CASCADE)
    ds = models.ForeignKey(data_source, related_name="data_source", on_delete=models.CASCADE)
    def __str__(self):
        return self.key_word
    class Meta:
        db_table = "sensor_name"