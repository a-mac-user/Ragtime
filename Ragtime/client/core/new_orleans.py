import os
import sys
import json
import datetime
import urllib.parse
import urllib.request
from urllib.request import urlopen
from core import api_token
from conf import settings
from core import info_cellection


class ArgvHandler(object):
    def __init__(self, argv_list):
        self.argvs = argv_list
        self.parse_argv()

    def parse_argv(self):
        if len(self.argvs) > 1:
            if hasattr(self, self.argvs[1]):
                func = getattr(self, self.argvs[1])
                func()
            else:
                self.help_msg()
        else:
            self.help_msg()

    def help_msg(self):
        msg = '''
        collect_data
        get_asset_id
        report_asset
        '''
        print(msg)

    def collect_data(self):
        # 收集数据不汇报
        obj = info_cellection.InfoCollection()
        asset_data = obj.collect()
        # print(asset_data)

    def report_asset(self):
        obj = info_cellection.InfoCollection()
        asset_data = obj.collect()

        asset_id = self.load_asset_id()
        if asset_id:  # 之前报告过
            asset_data['asset_id'] = asset_id
            post_url = 'asset_report'
        else:  # 第一次报告到服务器,扔到待审核区
            asset_data['asset_id'] = None
            post_url = 'asset_report_with_no_id'

        data = {'asset_data': json.dumps(asset_data)}
        response = self.__submit_data(post_url, data, method='post')
        if 'asset_id' in response:
            self.__update_asset_id(response['asset_id'])

        self.log_record(response)

    def load_asset_id(self):
        asset_id_file = settings.params['asset_id']
        has_asset_id = False
        if os.path.isfile(asset_id_file):
            asset_id = open(asset_id_file).read().strip()
            if asset_id.isdigit():
                return asset_id
            else:
                has_asset_id = False
        else:
            has_asset_id = False

    def log_record(self, log):
        f = open(settings.params["log_file"], "ab")
        if log is str:
            pass
        if type(log) is dict:

            if "info" in log:
                for msg in log["info"]:
                    log_format = "%s\tINFO\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    # print msg
                    f.write(bytes(log_format))
            if "error" in log:
                for msg in log["error"]:
                    log_format = "%s\tERROR\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(bytes(log_format))
            if "warning" in log:
                for msg in log["warning"]:
                    log_format = "%s\tWARNING\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(bytes(log_format))
        f.close()

    def __attach_token(self, url_str):
        # 利用token_id和用户名和时间戳生成md5, 并加在url
        user = settings.params['auth']['user']
        token_id = settings.params['auth']['token']

        md5_token, timestamp = api_token.get_token(user, token_id)
        url_arg_str = "user=%s&timestamp=%s&token=%s" % (user, timestamp, md5_token)
        if "?" in url_str:  # already has arg
            new_url = url_str + "&" + url_arg_str
        else:
            new_url = url_str + "?" + url_arg_str
        return new_url

    def __update_asset_id(self, new_asset_id):
        asset_id_file = settings.params['asset_id']
        f = open(asset_id_file, 'wb')
        f.write(bytes(new_asset_id))
        f.close()

    def __submit_data(self, url_name, data, method):
        if url_name in settings.params['urls']:
            if type(settings.params['port']) is int:
                url = 'http://%s:%s%s' % (settings.params['server'],
                                          settings.params['port'],
                                          settings.params['urls'][url_name],
                                          )
            else:
                url = 'http://%s%s' % (settings.params['server'],
                                       settings.params['urls'][url_name],)
            url = self.__attach_token(url)
            print('Connecting [%s], it may take a minute.' % settings.params['server'])
            if method == 'post':
                try:
                    data_encode = urllib.parse.urlencode(data).encode('utf-8')
                    req = urllib.request.Request(url=url,
                                                 data=data_encode)
                    res_data = urlopen(req,
                                       timeout=settings.params['request_timeout'])
                    callback = res_data.read()
                    callback = json.loads(callback)
                    print("\033[31;1m[%s]:[%s]\033[0m response:\n%s" % (method,
                                                                        url,
                                                                        callback))
                    return callback
                except Exception as e:
                    sys.exit("\033[31;1m%s\033[0m" % e)
            else:
                raise AttributeError
        else:
            raise KeyError
