import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

params = {
    "server": "localhost",
    "port": 8000,
    'request_timeout': 30,
    "urls": {
        "asset_report_with_no_id": "/asset/report/asset_with_no_asset_id/",
        "asset_report": "/asset/report/",
    },
    'asset_id': '%s/var/.asset_id' % BASE_DIR,
    'log_file': '%s/logs/run_log' % BASE_DIR,

    'auth': {
        'user': 'tom@126.com',
        'token': 'tom1'
    },
}
