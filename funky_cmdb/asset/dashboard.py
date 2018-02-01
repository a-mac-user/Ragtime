import random
from asset import models
from django.db.models import Count


class AssetDashboard(object):
    # 画图需要的数据都在这里生成
    def __init__(self, request):
        self.request = request
        self.asset_list = models.Asset.objects.all()
        self.data = {}

    def searilize_page(self):
        # 生成页面需要的数据
        self.data['asset_categories'] = self.get_asset_categories()
        self.data['asset_status_list'] = self.get_asset_status_statistics()
        self.data['business_load'] = self.get_business_load()

    def get_business_load(self):
        # 调用监控等系统(待开发)，得到每个业务线的负载率
        dataset = {
            'names': [],
            'data': [],
        }
        for obj in models.BusinessUnit.objects.filter(parent_level=None):
            load_val = random.randint(20, 95)  # 这是个模拟数据，模拟各业务线的使用率负载
            dataset['names'].append(obj.name)
            dataset['data'].append(load_val)
        return dataset

    def get_asset_status_statistics(self):
        # 资产状态分类统计
        queryset = list(self.asset_list.values('status').annotate(value=Count('status')))
        dataset = {
            'names': [],
            'data': []
        }
        for index, item in enumerate(queryset):  # 0,{}
            for db_val, display_name in models.Asset.status_choice:  # 0,'在线'
                if db_val == item['status']:
                    queryset[index]['name'] = display_name
        dataset['names'] = [item['name'] for item in queryset]
        dataset['data'] = [item['value'] for item in queryset]
        return dataset

    def get_asset_categories(self):
        # 按资产类型进行分类
        dataset = {
            'names': [],
            'data': []
        }
        prefetch_data = {
            models.Server: None,
            models.NetworkDevice: None,
            models.SecurityDevice: None,
            models.Software: None,
        }
        for key in prefetch_data:
            data_list = list(key.objects.values('sub_asset_type').annotate(total=Count('sub_asset_type')))
            for index, category in enumerate(data_list):
                for db_val, display_name in key.sub_asset_type_choices:
                    if category['sub_asset_type'] == db_val:
                        data_list[index]['name'] = display_name

            for item in data_list:
                dataset['names'].append(item['name'])
                dataset['data'].append(item['total'])
        return dataset
