from django.shortcuts import render

def dashboardAcc(request):
    return render(request, 'dashboardAcc.html')

def ordersAcc(request):
    return render(request, 'ordersAcc.html')

def buyorderAcc(request):
    return render(request, 'buyorderAcc.html')

def sellorderAcc(request):
    return render(request, 'sellorderAcc.html')

def unlistedSharesAcc(request):
    return render(request, 'unlistedSharesAcc.html')

def ShareListAcc(request):
    return render(request, 'ShareListAcc.html')

def clientAcc(request):
    return render(request, 'clientAcc.html')

def reportsAcc(request):
    return render(request, 'reportsAcc.html')

def buyOrderSummaryAcc(request):
    return render(request, 'buyOrderSummary.html')

def SellerSummaryAcc(request):
    return render(request, 'SellSummary.html')

def AngelInvestAcc(request):
    return render(request, 'AngelInvest.html')
