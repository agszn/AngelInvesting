from django.shortcuts import render

def baseStructure(request):
    return render(request, 'baseStructureRM.html')

def angelInvestRM(request):
    return render(request, 'angelInvestRM.html')

def buyorderRM(request):
    return render(request, 'buyorderRM.html')

def clientRM(request):
    return render(request, 'clientRM.html')

def ordersRM(request):
    return render(request, 'ordersRM.html')

def sellorderRM(request):
    return render(request, 'sellorderRM.html')

def ShareListRM(request):
    return render(request, 'ShareListRM.html')

def unlistedSharesRM(request):
    return render(request, 'unlistedSharesRM.html')

def dashboardRM(request):
    return render(request, 'dashboardRM.html')

def buyordersummeryRM(request):
    return render(request, 'buyordersummeryRM.html')

def selldersummeryRM(request):
    return render(request, 'selldersummeryRM.html')