from django.shortcuts import render

def dashboardST(request):
    return render(request, 'dashboardST.html')

def buyorderST(request):
    return render(request, 'buyorderST.html')

def buyOrderSummaryST(request):
    return render(request, 'buyOrderSummaryST.html')

def buyDealLetterrST(request):
    return render(request, 'buyDealLetterrST.html')

def sellorderST(request):
    return render(request, 'sellorderST.html')

def SellerSummaryST(request):
    return render(request, 'SellSummaryST.html')

def sellDealLetterrST(request):
    return render(request, 'sellDealLetterST.html')

def clientST(request):
    return render(request, 'clientST.html')

