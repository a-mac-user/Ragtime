import json
from asset import core
from asset import models
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def asset_with_no_asset_id(request):
    if request.method == 'POST':
        asset_handler = core.Asset(request)
        res = asset_handler.get_asset_id_by_sn()

        return HttpResponse(json.dumps(res))


def new_assets_approval(request):
    if request.method == 'POST':
        request.POST = request.POST.copy()  # 默认不能修改POST
        approval_asset_list = request.POST.getlist('approval_asset_list')
        approval_asset_list = models.NewAssetApprovalZone.objects.filter()

        response_dic = {}
        for obj in approval_asset_list:
            request.POST['asset_data'] = obj.data
            asset_handler = core.Asset(request)
            if asset_handler.data_is_valid_without_id():
                asset_handler.data_inject()
                obj.approved = True
                obj.save()

            response_dic[obj.id] = asset_handler.response

    return HttpResponse
