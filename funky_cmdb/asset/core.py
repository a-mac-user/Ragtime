import json
from asset import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class Asset(object):
    def __init__(self, request):
        self.request = request
        self.mandatory_fields = ['sn', 'asset_id', 'asset_type']
        self.field_sets = {
            'asset': ['manufactory'],
            'server': ['model',
                       'cpu_count',
                       'cpu_core_count',
                       'cpu_model',
                       'raid_type',
                       'os_type',
                       'os_distribution',
                       'os_release'],
            'networkdevice': []
        }
        self.response = {
            'error': [],
            'info': [],
            'warning': []
        }

    def get_asset_id_by_sn(self):
        data = self.request.POST.get('asset_data')
        if data:
            try:
                data = json.loads(data)
                if self.mandatory_check(data, only_check_sn=True):
                    response = {'asset_id': self.asset_obj.id}
                else:
                    if hasattr(self, 'waiting_approval'):
                        response = {'need_approval': "this is a new asset,needs IT admin's approval"
                                                     " to create the new asset id."}
                        self.clean_data = data
                        self.save_new_asset_to_approval_zone()
                    else:
                        response = self.response
            except ValueError as e:
                self.response_msg('error',
                                  'AssetDataInvalid',
                                  str(e))
                response = self.response
        else:
            self.response_msg('error',
                              'AssetDataInvalid',
                              "The reported asset data is not valid or provided")
            response = self.response
        return response

    def mandatory_check(self, data, only_check_sn=False):
        for field in self.mandatory_fields:
            if field not in data:
                self.response_msg('error',
                                  'MandatoryCheckFailed',
                                  "The field [%s] is mandatory and not provided in your reporting data" % field)
        else:
            if self.response['error']:
                return False
        try:
            if not only_check_sn:
                self.asset_obj = models.Asset.objects.get(id=int(data['asset_id']), sn=data['sn'])
            else:
                self.asset_obj = models.Asset.objects.get(sn=data['sn'])
            return True
        except ObjectDoesNotExist as e:
            self.response_msg('error',
                              'AssetDataInvalid',
                              "Cannot find asset object in DB by using asset id [%s] and SN [%s] " %
                              (data['asset_id'], data['sn']))
            self.waiting_approval = True
            return False

    def response_msg(self, msg_type, key, msg):
        if msg_type in self.response:
            self.response[msg_type].append({key: msg})
        else:
            raise ValueError

    def save_new_asset_to_approval_zone(self):
        asset_sn = self.clean_data.get('sn')
        asset_already_in_approval_zone = models.NewAssetApprovalZone.objects.\
            get_or_create(sn=asset_sn,
                          data=json.dumps(self.clean_data),
                          manufactory=self.clean_data.get('manufactory'),
                          model=self.clean_data.get('model'),
                          asset_type=self.clean_data.get('asset_type'),
                          ram_size=self.clean_data.get('ram_size'),
                          cpu_model=self.clean_data.get('cpu_model'),
                          cpu_count=self.clean_data.get('cpu_count'),
                          cpu_core_count=self.clean_data.get('cpu_core_count'),
                          os_distribution=self.clean_data.get('os_distribution'),
                          os_release=self.clean_data.get('os_release'),
                          os_type=self.clean_data.get('os_type'),)
        return True

    def data_is_valid_without_id(self):
        # 如果汇报过来的资产没有资产id，走这个方法
        data = self.request.POST.get('asset_data')
        if data:
            try:
                data = json.loads(data)
                asset_obj = models.Asset.objects.get_or_create(sn=data.get['sn'])
                data['asset_id'] = asset_obj[0].id
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response['error']:
                    return True
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error',
                              'AssetDataInvalid',
                              "The reported asset data is not valid or provided")

    def data_inject(self):
        # 开始存数据到数据库,data_is_valid()必须为真,才能执行本函数
        if self.__is_new_asset():
            print('---new asset,going to create----')
            self.create_asset()
        else:
            print('---asset already exist ,going to update----')
            self.update_asset()

    def __is_new_asset(self):
        if not hasattr(self.asset_obj, self.clean_data['asset_type']):
            # 如果有这个外键关系，就代表是老资产
            return True
        else:
            return False

    def create_asset(self):
        func = getattr(self, '_create_%s' % self.clean_data['asset_type'])
        create_obj = func()

    def update_asset(self):
        func = getattr(self, '_update_%s' % self.clean_data['asset_type'])
        update_obj = func()

    def _create_server(self):
        self.__create_server_info()
        self.__create_or_update_manufactory()
        self.__create_cpu_component()

        self.__create_disk_component()
        self.__create_nic_component()
        self.__create_ram_component()

        log_msg = "Asset [<a href='/admin/assets/asset/%s/' target='_blank'>%s</a>] has been created!" %\
                  (self.asset_obj.id, self.asset_obj)
        self.response_msg('info', 'NewAssetOnline', log_msg)

    def __verify_field(self, data_set, field_key, data_type, required=True):
        field_val = data_set.get(field_key)
        if field_val:
            try:
                data_set[field_key] = data_type(field_val)
            except ValueError as e:
                self.response_msg('error',
                                  'InvalidField',
                                  "The field [%s]'s data type is invalid,the correct data type should be [%s] " %
                                  (field_key, data_type))
        elif required:
            self.response_msg('error',
                              'LackOfField',
                              "The field [%s] has no value provided in your reporting data [%s]" %
                              (field_key, data_set))

    def __create_server_info(self, ignore_errs=False):
        # 创建server表的相关信息,第一步进行小字典的合法验证
        try:
            self.__verify_field(self.clean_data, 'model', str)
            if not len(self.response['error']) or ignore_errs is True:
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'raid_type': self.clean_data.get('raid_type'),
                    'os_type': self.clean_data.get('os_type'),
                    'os_distribution': self.clean_data.get('os_distribution'),
                    'os_release': self.clean_data.get('os_release'),
                }
                obj = models.Server(**data_set)
                obj.asset.model = self.clean_data.get('model')
                obj.save()
                return obj
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [server] %s' % str(e))

    def __create_or_update_manufactory(self, ignore_errs=False):
        # 创建Manufactory表的相关信息,第一步进行验证
        try:
            self.__verify_field(self.clean_data, 'manufactory', str)
            manufactory = self.clean_data.get('manufactory')
            if not len(self.response['error']) or ignore_errs is True:
                obj_exist = models.Manufactory.objects.filter(manufactory=manufactory)
                if obj_exist:
                    obj = obj_exist[0]
                else:
                    obj = models.Manufactory(manufactory=manufactory)
                    obj.save()
                obj.asset_obj.manufactory = obj
                obj.asset_obj.save()
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [manufactory] %s' % str(e))

    def __create_cpu_component(self, ignore_errs=False):
        try:
            self.__verify_field(self.clean_data, 'model', str)
            self.__verify_field(self.clean_data, 'cpu_count', str)
            self.__verify_field(self.clean_data, 'cpu_core_count', str)
            if not len(self.response['error']) or ignore_errs is True:
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'model': self.clean_data.get('model'),
                    'cpu_count': self.clean_data.get('cpu_count'),
                    'cpu_core_count': self.clean_data.get('cpu_core_count'),
                }
                obj = models.CPU(**data_set)
                obj.save()
                self.response_msg('info',
                                  'NewComponentAdded',
                                  "Asset[%s] --> has added new [cpu] component with data [%s]" %
                                  (self.asset_obj, data_set))
                return obj
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [server] %s' % str(e))

    def __create_disk_component(self):
        disk_info = self.clean_data.get('physical_disk_driver')
        if disk_info:
            for disk_item in disk_info:
                try:
                    self.__verify_field(disk_item, 'slot', str)
                    self.__verify_field(disk_item, 'capacity', float)
                    self.__verify_field(disk_item, 'iface_type', str)
                    self.__verify_field(disk_item, 'model', str)
                    if not len(self.response['error']):  # no processing when there's no error happend
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'sn': disk_item.get('sn'),
                            'slot': disk_item.get('slot'),
                            'capacity': disk_item.get('capacity'),
                            'model': disk_item.get('model'),
                            'iface_type': disk_item.get('iface_type'),
                            'manufactory': disk_item.get('manufactory'),
                        }
                        obj = models.Disk(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [disk] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'Disk info is not provided in your reporting data')

    def __create_nic_component(self):
        nic_info = self.clean_data.get('nic')
        if nic_info:
            for nic_item in nic_info:
                try:
                    self.__verify_field(nic_item, 'macaddress', str)
                    if not len(self.response['error']):
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'name': nic_item.get('name'),
                            'sn': nic_item.get('sn'),
                            'macaddress': nic_item.get('macaddress'),
                            'ipaddress': nic_item.get('ipaddress'),
                            'bonding': nic_item.get('bonding'),
                            'model': nic_item.get('model'),
                            'netmask': nic_item.get('netmask'),
                        }
                        obj = models.NIC(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [nic] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'NIC info is not provided in your reporting data')

    def __create_ram_component(self):
        ram_info = self.clean_data.get('ram')
        if ram_info:
            for ram_item in ram_info:
                try:
                    self.__verify_field(ram_item, 'capacity', int)
                    if not len(self.response['error']):
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'slot': ram_item.get("slot"),
                            'sn': ram_item.get('sn'),
                            'capacity': ram_item.get('capacity'),
                            'model': ram_item.get('model'),
                        }
                        obj = models.RAM(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [ram] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'RAM info is not provided in your reporting data')
