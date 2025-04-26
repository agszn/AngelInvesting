from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import *
import json
from django.utils.timezone import localtime


@login_required
def stock_list(request):
    query = request.GET.get('q', '')
    stocks = StockData.objects.filter(company_name__icontains=query) if query else StockData.objects.all()
    return render(request, 'stocks/stock_list.html', {'stocks': stocks, 'query': query})

# @login_required
# def stock_detail(request, stock_id):
#     stock = get_object_or_404(StockData, id=stock_id)
#     price_history = StockHistory.objects.filter(stock=stock).order_by('timestamp')

#     if not price_history.exists():
#         print("❌ No stock history found for this stock.")
    
#     stock_dates = [
#         localtime(timestamp).strftime('%Y-%m-%d')
#         for timestamp in price_history.values_list('timestamp', flat=True)
#         if timestamp is not None
#     ]

#     stock_prices = [float(price) for price in price_history.values_list('price', flat=True)]

#     # Fetching related directors
#     directors = stock.directors.all()  # Use related_name="directors" from ForeignKey in Director model
#     stock_searched = StockData.objects.order_by('-number_of_times_searched').first()
#     # Calculate the percentage difference in the view
#     if stock_searched and stock_searched.share_price is not None and stock_searched.ltp is not None:
#         percentage_diff = ((stock_searched.ltp - stock_searched.share_price) / stock_searched.share_price) * 100
#     else:
#         percentage_diff = 0


#     context = {
#         'stock': stock,
#         'directors': directors,
#         'stock_searched':stock_searched,
#         'percentage_diff': percentage_diff,
#         'stock_dates': json.dumps(stock_dates),
#         'stock_prices': json.dumps(stock_prices),
#     }
#     return render(request, 'stocks/stock_detail.html', context)


# @login_required
# def stock_detail(request, stock_id):
#     stock = get_object_or_404(StockData, id=stock_id)
#     price_history = StockHistory.objects.filter(stock=stock).order_by('timestamp')

#     if not price_history.exists():
#         print("❌ No stock history found for this stock.")

#     stock_dates = [
#         localtime(timestamp).strftime('%Y-%m-%d')
#         for timestamp in price_history.values_list('timestamp', flat=True)
#         if timestamp is not None
#     ]

#     stock_prices = [float(price) for price in price_history.values_list('price', flat=True)]

#     # Fetching related directors
#     directors = stock.directors.all()
    
#     # Fetch the most searched stock
#     stock_searched = StockData.objects.order_by('-number_of_times_searched').first()
    
#     if stock_searched and stock_searched.share_price is not None and stock_searched.ltp is not None:
#         percentage_diff = ((stock_searched.ltp - stock_searched.share_price) / stock_searched.share_price) * 100
#     else:
#         percentage_diff = 0

#     # Fetching Balance Sheet Data
#     balance_sheets = BalanceSheet.objects.filter(stock_period__stock=stock).order_by('stock_period__stock_date')

#     balance_sheet_data = {}
#     headers = ["Particulars"]
#     for bs in balance_sheets:
#         stock_date = bs.stock_period.stock_date.strftime('%Y-%m-%d')
#         headers.append(stock_date)

#         for field in BalanceSheet._meta.fields:
#             if field.name not in ["id", "stock_period", "total_equity_and_liabilities", "total_assets"]:
#                 if field.verbose_name not in balance_sheet_data:
#                     balance_sheet_data[field.verbose_name] = []
#                 balance_sheet_data[field.verbose_name].append(getattr(bs, field.name, 0))

#     # Fetching Profit & Loss Statement Data
#     profit_loss_statements = ProfitLossStatement.objects.filter(stock_period__stock=stock).order_by('stock_period__stock_date')

#     profit_loss_data = {}
#     pl_headers = ["Particulars"]
#     for pls in profit_loss_statements:
#         stock_date = pls.stock_period.stock_date.strftime('%Y-%m-%d')
#         pl_headers.append(stock_date)

#         for field in ProfitLossStatement._meta.fields:
#             if field.name not in ["id", "stock_period"]:
#                 if field.verbose_name not in profit_loss_data:
#                     profit_loss_data[field.verbose_name] = []
#                 profit_loss_data[field.verbose_name].append(getattr(pls, field.name, 0))

#     # Fetching Cash Flow Statement Data
#     cash_flows = CashFlow.objects.filter(stock_period__stock=stock).order_by('stock_period__stock_date')


#     cash_flow_data = {}
#     cf_headers = ["Particulars"]
#     for cf in cash_flows:
#         stock_date = cf.stock_period.stock_date.strftime('%Y-%m-%d')
#         cf_headers.append(stock_date)

#         for field in CashFlow._meta.fields:
#             if field.name not in ["id", "stock_period"]:
#                 if field.verbose_name not in cash_flow_data:
#                     cash_flow_data[field.verbose_name] = []
#                 cash_flow_data[field.verbose_name].append(getattr(cf, field.name, 0))


#     stock_holder = get_object_or_404(StockData, pk=stock_id)
#     shareholdings = stock_holder.shareholdings.all()  # uses related_name

#     context = {
#         'stock': stock,
#         'directors': directors,
#         'stock_searched': stock_searched,
#         'percentage_diff': percentage_diff,
#         'stock_dates': json.dumps(stock_dates),
#         'stock_prices': json.dumps(stock_prices),
#         'headers': headers,
#         'balance_sheet_data': balance_sheet_data,
#         'pl_headers': pl_headers,
#         'profit_loss_data': profit_loss_data,
#         'cf_headers': cf_headers,
#         'cash_flow_data': cash_flow_data,
#         'cash_flows':cash_flows,
#         'stock_holder': stock_holder,
#         'shareholdings': shareholdings
#     }
#     return render(request, 'stocks/stock_detail.html', context)

@login_required
def stock_detail(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    price_history = StockHistory.objects.filter(stock=stock).order_by('timestamp')

    if not price_history.exists():
        print("❌ No stock history found for this stock.")

    stock_dates = [
        localtime(timestamp).strftime('%Y-%m-%d')
        for timestamp in price_history.values_list('timestamp', flat=True)
        if timestamp is not None
    ]
    
    stock_prices = [float(price) for price in price_history.values_list('price', flat=True)]

    # 
    # 
    # 
    # Fetching related directors
    # 
    # 
    directors = stock.directors.all()

    # 
    # 
    # 
    # Fetch the most searched stocks
    # 
    # 
    stock_searched = StockData.objects.order_by('-number_of_times_searched').first()

    if stock_searched and stock_searched.share_price is not None and stock_searched.ltp is not None:
        percentage_diff = ((stock_searched.ltp - stock_searched.share_price) / stock_searched.share_price) * 100
    else:
        percentage_diff = 0


    stock_holder = get_object_or_404(StockData, pk=stock_id)
    shareholdings = stock_holder.shareholdings.all()  # uses related_name

    # Fetching multiple stocks to display in the cards section
    all_stocks = StockData.objects.all()  # Fetch all stocks or customize this query as needed

    # 
    # 
    # 
    # balance sheet, cashflow, and other tables
    # 
    # 
    # 
    selected_stock = StockData.objects.get(id=stock_id)

    field_definitions = CustomFieldDefinition.objects.all()


    headers = TableHeader.objects.filter(
        custom_field_values__stock=selected_stock,
        custom_field_values__field_definition__in=field_definitions
    ).distinct().order_by('order')

    all_values = CustomFieldValue.objects.filter(
        stock=selected_stock,
        field_definition__in=field_definitions
    ).select_related('field_definition', 'table_header')

    # 
    # 
    # 
    # 
    # report
    # 
    # 
    # 
    reports = Report.objects.filter(stock=stock)  

    #  company subsidiary and associate    
    relations = stock.related_companies.all()

        # 
    # 
    # 
    # 
    # PrincipalBusinessActivity
    # 
    # 
    # principalBusinessActivity = StockData.PrincipalBusinessActivity.all()
    principal_activities = stock.business_activities.all()
    # 
    # company FAQ
    faqs = stock.faqs.all()
    context = {
        'stock': stock,
        'directors': directors,
        'stock_searched': stock_searched,
        'percentage_diff': percentage_diff,
        'stock_dates': json.dumps(stock_dates),
        'stock_prices': json.dumps(stock_prices),

        'stock_holder': stock_holder,
        'shareholdings': shareholdings,

        'all_stocks': all_stocks, 
        
        'selected_stock': selected_stock,
        'headers': headers,
        'field_definitions': field_definitions,
        'all_values': all_values,

        'reports': reports,

        'relations': relations,

        'faqs': faqs,

        'principalBusinessActivity':principal_activities,

    }
    return render(request, 'stocks/stock_detail.html', context)


@login_required
def angelStockListing(request):
    stocks = StockData.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        stocks = stocks.filter(company_name__icontains=search_query)
    
    selected_sector = request.GET.get('sector', '')
    if selected_sector:
        stocks = stocks.filter(sector=selected_sector)

    paginator = Paginator(stocks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    stock_history_data = {}
    for stock in page_obj:
        history = StockHistory.objects.filter(stock=stock).order_by('-timestamp')[:100]
        stock_history_data[stock.id] = list(history.values('timestamp', 'price'))

    sectors = StockData.objects.values_list('sector', flat=True).distinct()

    return render(request, 'AngelStockList/stockList.html', {
        'page_obj': page_obj,
        'stock_history_data': json.dumps(stock_history_data, default=str),
        'sectors': sectors,
        'search_query': search_query,
        'selected_sector': selected_sector
    })

# navbarMarquee
def stock_ticker_view(request):
    stocks = StockData.objects.all()

    # Calculate percentage difference and store it in a new attribute
    for stock in stocks:
        if stock.ltp and stock.share_price and stock.share_price > 0:
            stock.percentage_diff = ((stock.ltp - stock.share_price) / stock.share_price) * 100
        else:
            stock.percentage_diff = None  # Handle missing or zero share price

    return render(request, "navbar/navbar.html", {"stocks": stocks})


# 
# 
# def all_data_view(request, stock_id=None):
#     stock_periods = StockPeriod.objects.all().order_by('-year', '-month', '-day')
#     table_headers = TableHeader.objects.prefetch_related('fields').all()
#     field_definitions = CustomFieldDefinition.objects.all()

#     custom_values = CustomFieldValue.objects.select_related(
#         'stock', 'stock_period', 'field_definition', 'table_header'
#     )
    
#     if stock_id:
#         custom_values = custom_values.filter(stock_id=stock_id)

#     # Get distinct stock list
#     stock_list = StockData.objects.filter(
#         id__in=custom_values.values_list('stock_id', flat=True).distinct()
#     )

#     context = {
#         'stock_periods': stock_periods,
#         'table_headers': table_headers,
#         'field_definitions': field_definitions,
#         'custom_values': custom_values,
#         'stock_list': stock_list,
#         'selected_stock_id': int(stock_id) if stock_id else None,
#     }
#     return render(request, 'balance_sheet.html', context)

# -------------------------------------------------
# -------------------------------------------------

# -------------------------------------------------
# -------------------------------------------------
# def balance_sheet_view(request):
#     field_definitions = CustomFieldDefinition.objects.filter(model_type='BALANCE_SHEET')
#     table_headers = TableHeader.objects.all()
#     custom_values_qs = CustomFieldValue.objects.filter(field_definition__in=field_definitions)

#     # Create a nested dict: stock -> field_id -> header_id -> value
#     custom_values = defaultdict(lambda: defaultdict(dict))
#     stocks = set()

#     for val in custom_values_qs:
#         custom_values[val.stock][val.field_definition_id][val.table_header_id] = val
#         stocks.add(val.stock)

#     context = {
#         "field_definitions": field_definitions,
#         "table_headers": table_headers,
#         "custom_values": custom_values,
#         "stocks": sorted(stocks, key=lambda x: str(x)),
#     }
#     return render(request, "balance_sheet.html", context)


def balance_sheet_view(request, stock_id):
    selected_stock = StockData.objects.get(id=stock_id)

    field_definitions = CustomFieldDefinition.objects.all()

    headers = TableHeader.objects.filter(
        custom_field_values__stock=selected_stock,
        custom_field_values__field_definition__in=field_definitions
    ).distinct().order_by('order')

    all_values = CustomFieldValue.objects.filter(
        stock=selected_stock,
        field_definition__in=field_definitions
    ).select_related('field_definition', 'table_header')

    context = {
        'selected_stock': selected_stock,
        'headers': headers,
        'field_definitions': field_definitions,
        'all_values': all_values,
    }
    return render(request, 'balance_sheet.html', context)
