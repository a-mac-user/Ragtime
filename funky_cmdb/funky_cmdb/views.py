from asset import table
from asset import models, admin
from django.contrib import auth
from django.utils import timezone
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def acc_login(request):
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.valid_end_time:  # 设置了end time
                if user.valid_begin_time < timezone.now() < user.valid_end_time:
                    auth.login(request, user)
                    request.session.set_expiry(60*300)
                    return HttpResponseRedirect('/')
                else:
                    return render(request,
                                  'login.html',
                                  {'login_err': 'User account is expired,please contact your IT guy for this!'})
            elif timezone.now() > user.valid_begin_time:
                    auth.login(request, user)
                    request.session.set_expiry(60*300)
                    return HttpResponseRedirect('/')
        else:
            return render(request,
                          'login.html',
                          {'login_err': 'Wrong username or password'})
    else:
        return render(request, 'login.html')


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def charts(request):
    return render(request, 'charts.html')


@login_required
def tables(request):
    asset_obj_list = table.table_filter(request, admin.AssetAdmin, models.Asset)

    order_res = table.get_order_by(request, asset_obj_list, admin.AssetAdmin)

    paginator = Paginator(order_res[0], admin.AssetAdmin.list_per_page)
    page = request.GET.get('page')
    try:
        asset_obj = paginator.page(page)
    except PageNotAnInteger:
        asset_obj = paginator.page(1)
    except EmptyPage:
        asset_obj = paginator.page(paginator.num_pages)

    table_obj = table.TableHandler(request,
                                   models.Asset,
                                   admin.AssetAdmin,
                                   asset_obj,
                                   order_res
                                   )
    return render(request,
                  'tables.html',
                  {'table_obj': table_obj, 'paginator': paginator})


@login_required
def events(request):
    return render(request, 'events.html')


def test(request):
    return render(request, 'test.html')