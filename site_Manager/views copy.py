from django.shortcuts import render
from django.contrib.auth.decorators import login_required
def BlogSM(request):
    return render(request, 'BlogSM.html')

# views.py

from django.shortcuts import render, redirect
from .models import HeroSectionBanner
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from .models import *
from unlisted_stock_marketplace.models import *

@login_required
def HomepageBannerSM(request):
    banner = HeroSectionBanner.objects.filter(is_active=True).first()

    if request.method == 'POST' and request.FILES.get('banner'):
        # Deactivate previous banners
        HeroSectionBanner.objects.filter(is_active=True).update(is_active=False)
        
        new_banner = HeroSectionBanner.objects.create(
            image=request.FILES['banner'],
            is_active=True
        )
        return redirect('SM_User:HomepageBannerSM')  # refresh page

    return render(request, 'HomepageBannerSM.html', {'banner': banner})

from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.urls import reverse

@require_POST
def delete_banner(request):
    HeroSectionBanner.objects.filter(is_active=True).delete()
    return redirect('SM_User:HomepageBannerSM') 

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import csv, io
from django.http import HttpResponse

from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .forms import *


# @login_required
# def UnlistedStocksUpdateSM(request):
#     today = timezone.now().date()

#     if request.method == "POST":
#         stock_id = request.POST.get('stock_id')
#         share_price_str = request.POST.get('share_price')
#         conviction_level = request.POST.get('conviction_level')
#         lot_size_str = request.POST.get('lot_size')

#         if stock_id:
#             stock = get_object_or_404(StockData, pk=stock_id)

#             # Only update lot_size directly in StockData
#             try:
#                 lot_size = int(lot_size_str) if lot_size_str else None
#                 if lot_size is not None:
#                     stock.lot = lot_size
#                     stock.save()
#             except (ValueError, TypeError):
#                 pass  # Ignore invalid lot sizes

#             # Create or update the snapshot for today
#             snapshot, _ = StockDailySnapshot.objects.get_or_create(stock=stock, date=today)

#             try:
#                 share_price = Decimal(share_price_str) if share_price_str else None
#                 if share_price is not None:
#                     snapshot.share_price = share_price
#             except (InvalidOperation, TypeError):
#                 pass

#             if conviction_level:
#                 snapshot.conviction_level = conviction_level

#             snapshot.save(update_stockdata=False)

#             return redirect('SM_User:UnlistedStocksUpdateSM')

#     # Handle GET request
#     query = request.GET.get('q', '').strip()
#     all_stocks = StockData.objects.all()

#     if query:
#         all_stocks = all_stocks.filter(Q(company_name__icontains=query) | Q(sector__icontains=query))

#     snapshots = []
#     for stock in all_stocks:
#         snapshot = StockDailySnapshot.objects.filter(stock=stock, date=today).first()
#         if snapshot:
#             snapshots.append(snapshot)
#         else:
#             # Fallback to the most recent snapshot, or a placeholder with today's date
#             latest_snapshot = StockDailySnapshot.objects.filter(stock=stock).order_by('-date').first()
#             snapshots.append(latest_snapshot or StockDailySnapshot(stock=stock, date=today))

#     # Optional: Display CSV upload result feedback
#     upload_result = request.session.pop('csv_update_result', None)

#     return render(request, 'UnlistedStocksUpdateSM.html', {
#         'snapshots': snapshots,
#         'conviction_choices': CONVICTION_CHOICES,
#         'search_query': query,
#         'today': today,
#         'upload_result': upload_result,
#     })


from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.db.models import Q


@login_required
def UnlistedStocksUpdateSM(request):
    today = timezone.now().date()

    if request.method == "POST":
        stock_id = request.POST.get('stock_id')
        share_price_str = request.POST.get('share_price')
        ltp_str = request.POST.get('ltp')
        conviction_level = request.POST.get('conviction_level')
        lot_size_str = request.POST.get('lot_size')
        company_name = request.POST.get('company_name')
        sector = request.POST.get('sector')

        if stock_id:
            stock = get_object_or_404(StockData, pk=stock_id)

            # Update editable stock fields
            if company_name:
                stock.company_name = company_name
            if sector:
                stock.sector = sector
            try:
                lot_size = int(lot_size_str) if lot_size_str else None
                if lot_size is not None:
                    stock.lot = lot_size
            except (ValueError, TypeError):
                pass

            stock.save()

            # Create or update snapshot
            snapshot, _ = StockDailySnapshot.objects.get_or_create(stock=stock, date=today)

            try:
                ltp = Decimal(ltp_str) if ltp_str else None
                if ltp is not None:
                    snapshot.ltp = ltp
            except (InvalidOperation, TypeError):
                pass

            try:
                share_price = Decimal(share_price_str) if share_price_str else None
                if share_price is not None:
                    snapshot.share_price = share_price
            except (InvalidOperation, TypeError):
                pass

            if conviction_level:
                snapshot.conviction_level = conviction_level

            snapshot.save(update_stockdata=False)

        return redirect('SM_User:UnlistedStocksUpdateSM')  # ✅ RETURN FIXED

    # --- GET request handling ---
    query = request.GET.get('q', '').strip()
    all_stocks = StockData.objects.all()
    if query:
        all_stocks = all_stocks.filter(Q(company_name__icontains=query) | Q(sector__icontains=query))

    snapshots = []
    for stock in all_stocks:
        snapshot = StockDailySnapshot.objects.filter(stock=stock, date=today).first()
        if snapshot:
            snapshots.append(snapshot)
        else:
            latest_snapshot = StockDailySnapshot.objects.filter(stock=stock).order_by('-date').first()
            snapshots.append(latest_snapshot or StockDailySnapshot(stock=stock, date=today))

    upload_result = request.session.pop('csv_update_result', None)

    return render(request, 'UnlistedStocksUpdateSM.html', {
        'snapshots': snapshots,
        'conviction_choices': CONVICTION_CHOICES,
        'search_query': query,
        'today': today,
        'upload_result': upload_result,
    })


from django.db.models import Max
@login_required
def download_unlisted_stocks_csv(request):
    # Get the latest snapshot date per stock
    latest_dates = (
        StockDailySnapshot.objects
        .values('stock')
        .annotate(latest_date=Max('date'))
    )

    # Build a dictionary {stock_id: latest_date}
    latest_date_map = {item['stock']: item['latest_date'] for item in latest_dates}

    # Query snapshots matching the latest date per stock
    latest_snapshots = StockDailySnapshot.objects.filter(
        *[
            # For each stock, filter snapshot on stock=stock_id and date=latest_date
            # But Django ORM can’t do this in a single query without subqueries
            # So do a filter with Q or subquery here:
            # We'll use a Q expression below
        ]
    )

    # The above approach is tricky in one query, so simpler approach:
    # Get all latest snapshots with a subquery:

    from django.db.models import OuterRef, Subquery

    latest_snapshot_subquery = StockDailySnapshot.objects.filter(
        stock=OuterRef('stock')
    ).order_by('-date').values('pk')[:1]

    latest_snapshots = StockDailySnapshot.objects.filter(
        pk__in=Subquery(latest_snapshot_subquery)
    ).select_related('stock')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="unlisted_stocks_update.csv"'

    writer = csv.writer(response)
    writer.writerow(['Company Name', 'Conviction Level', 'Share Price'])

    for snapshot in latest_snapshots:
        # Filter only unlisted stocks if needed:
        if snapshot.stock.stock_type == 'Unlisted':
            writer.writerow([snapshot.stock.company_name, snapshot.conviction_level, snapshot.share_price])

    return response

@login_required
def upload_unlisted_stocks_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        updated = 0
        skipped_names = []
        updated_ids = []
        today = timezone.now().date()

        for row in reader:
            name = row.get('Company Name')
            conviction = row.get('Conviction Level')
            price = row.get('Share Price')

            if not name:
                continue

            stock = StockData.objects.filter(company_name__iexact=name.strip()).first()
            if not stock:
                skipped_names.append(name.strip())
                continue

            try:
                price_decimal = Decimal(price.strip()) if price else None
            except (InvalidOperation, TypeError):
                skipped_names.append(name.strip())
                continue

            snapshot, _ = StockDailySnapshot.objects.get_or_create(stock=stock, date=today)

            if conviction:
                snapshot.conviction_level = conviction.strip()
            if price_decimal is not None:
                snapshot.share_price = price_decimal

            snapshot.save()
            updated_ids.append(snapshot.stock.id)
            updated += 1

        request.session['csv_update_result'] = {
            'updated_ids': updated_ids,
            'skipped_names': skipped_names,
            'updated_count': updated
        }

        return redirect('SM_User:UnlistedStocksUpdateSM')

    return redirect('SM_User:UnlistedStocksUpdateSM')


# update excel
import pandas as pd
import re
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from unlisted_stock_marketplace.models import StockData, StockDailySnapshot
import pandas as pd
import re
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

import openpyxl
import openpyxl
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt

import openpyxl
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import openpyxl
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from difflib import get_close_matches
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
import openpyxl
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# @login_required
# @csrf_exempt
# def upload_unlisted_stocks_excel(request):
#     if request.method == 'POST' and request.FILES.get('excel_file'):
#         excel_file = request.FILES['excel_file']
#         wb = openpyxl.load_workbook(excel_file)
#         sheet = wb.active

#         today = timezone.now().date()
#         yesterday = today - timezone.timedelta(days=1)

#         updated_ids = []
#         skipped_names = []
#         failed_updates = []
#         newly_added = []
#         fallback_ids = []  # for rows with 0 fallback

#         for idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
#             try:
#                 company_name = str(row[1].value).strip() if row[1].value else None
#                 raw_conviction = str(row[2].value).strip() if row[2].value else None
#                 conviction_level = raw_conviction.title() if raw_conviction else None
#                 price_today = row[3].value
#                 price_yesterday = row[4].value
#                 lot_size = row[5].value

#                 if not company_name:
#                     continue

#                 stock = StockData.objects.filter(company_name__iexact=company_name).first()
#                 if not stock:
#                     stock = StockData.objects.filter(scrip_name__iexact=company_name).first()

#                 if not stock:
#                     # Suggest similar names
#                     all_names = list(StockData.objects.values_list('company_name', flat=True)) + \
#                                 list(StockData.objects.values_list('scrip_name', flat=True))
#                     close = get_close_matches(company_name, all_names, n=3, cutoff=0.8)
#                     if close:
#                         skipped_names.append(company_name)
#                         continue

#                     # Create new StockData
#                     stock = StockData.objects.create(
#                         company_name=company_name,
#                         scrip_name=company_name,
#                         lot=int(lot_size) if lot_size else 100
#                     )
#                     newly_added.append(company_name)

#                 # Create/update yesterday snapshot
#                 try:
#                     ltp = Decimal(price_yesterday) if price_yesterday else Decimal('0.00')
#                 except (InvalidOperation, TypeError):
#                     ltp = Decimal('0.00')
#                     fallback_ids.append(str(stock.id))

#                 StockDailySnapshot.objects.get_or_create(
#                     stock=stock,
#                     date=yesterday,
#                     defaults={'share_price': ltp}
#                 )

#                 # Create or update today's snapshot
#                 snapshot, _ = StockDailySnapshot.objects.get_or_create(stock=stock, date=today)

#                 if conviction_level:
#                     if not snapshot.conviction_level or snapshot.conviction_level != conviction_level:
#                         snapshot.conviction_level = conviction_level

#                 try:
#                     share_price = Decimal(price_today) if price_today else Decimal('0.00')
#                 except (InvalidOperation, TypeError):
#                     share_price = Decimal('0.00')
#                     fallback_ids.append(str(stock.id))

#                 snapshot.share_price = share_price

#                 try:
#                     lot = int(lot_size) if lot_size else 0
#                 except (ValueError, TypeError):
#                     lot = 0
#                     fallback_ids.append(str(stock.id))

#                 snapshot.lot = lot

#                 snapshot.save()
#                 updated_ids.append(str(stock.id))

#             except Exception as e:
#                 failed_updates.append(f"{company_name}: {str(e)}")

#         context = {
#             'upload_result': {
#                 'updated_ids': updated_ids,
#                 'skipped_names': skipped_names,
#                 'failed_updates': failed_updates,
#                 'newly_added': newly_added,
#                 'fallback_ids': fallback_ids,  # for highlighting fallback 0 values
#             }
#         }
#         return render(request, 'UnlistedStocksUpdateSM.html', context)

#     return redirect('SM_User:UnlistedStocksUpdateSM')


from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
import openpyxl
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import pandas as pd
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import pandas as pd
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import pandas as pd
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import pandas as pd
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import pandas as pd
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import pandas as pd
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def upload_unlisted_stocks_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file, header=[0, 1])  # MultiIndex header

        price_columns = [
            col for col in df.columns
            if col[0] == 'PRICE' and pd.notnull(col[1])
        ]

        try:
            price_columns_sorted = sorted(
                price_columns,
                key=lambda x: pd.to_datetime(x[1])
            )
        except Exception:
            return render(request, 'UnlistedStocksUpdateSM.html', {
                'upload_result': {
                    'updated_ids': [],
                    'skipped_names': [],
                    'failed_updates': ['❌ Failed to sort PRICE columns. Ensure Excel subheaders are date formatted.'],
                    'newly_added': [],
                    'fallback_ids': [],
                }
            })

        if len(price_columns_sorted) < 2:
            return render(request, 'UnlistedStocksUpdateSM.html', {
                'upload_result': {
                    'updated_ids': [],
                    'skipped_names': [],
                    'failed_updates': ['❌ At least two PRICE columns with valid dates required.'],
                    'newly_added': [],
                    'fallback_ids': [],
                }
            })

        # Get date info
        yesterday_col = price_columns_sorted[-2]
        today_col = price_columns_sorted[-1]
        today_date = pd.to_datetime(today_col[1]).date()
        yesterday_date = pd.to_datetime(yesterday_col[1]).date()

        updated_ids, skipped_names, failed_updates = [], [], []
        newly_added, fallback_ids = [], []

        for idx, row in df.iterrows():
            try:
                company_name = conviction_level = None
                price_today = price_yesterday = lot_size = None

                for (main_header, sub_header), value in row.items():
                    if main_header == 'COMPANY NAME':
                        company_name = str(value).strip() if value else None
                    elif main_header == 'CONVICTION LEVEL':
                        conviction_level = str(value).strip().title() if value else None
                    elif main_header == 'LOT SIZE':
                        lot_size = value
                    elif (main_header, sub_header) == today_col:
                        price_today = value
                    elif (main_header, sub_header) == yesterday_col:
                        price_yesterday = value

                if not company_name:
                    continue

                stock = (
                    StockData.objects.filter(company_name__iexact=company_name).first()
                    or StockData.objects.filter(scrip_name__iexact=company_name).first()
                )

                if not stock:
                    all_names = list(StockData.objects.values_list('company_name', flat=True)) + \
                                list(StockData.objects.values_list('scrip_name', flat=True))
                    close = get_close_matches(company_name, all_names, n=3, cutoff=0.8)
                    if close:
                        skipped_names.append(company_name)
                        continue

                    stock = StockData.objects.create(
                        company_name=company_name,
                        scrip_name=company_name,
                        lot=int(lot_size) if lot_size else 100
                    )
                    newly_added.append(company_name)

                # Convert fields
                try:
                    share_price = Decimal(price_today) if price_today else Decimal('0.00')
                except (InvalidOperation, TypeError):
                    share_price = Decimal('0.00')
                    fallback_ids.append(str(stock.id))

                try:
                    ltp = Decimal(price_yesterday) if price_yesterday else Decimal('0.00')
                except (InvalidOperation, TypeError):
                    ltp = Decimal('0.00')
                    fallback_ids.append(str(stock.id))

                try:
                    lot = int(lot_size) if lot_size else 0
                except (ValueError, TypeError):
                    lot = 0
                    fallback_ids.append(str(stock.id))

                # 🔍 Debugging log
                print(f"🔄 Row {idx+2} | {company_name}")
                print(f"   📅 Today Price ({today_date}): {price_today} → {share_price}")
                print(f"   📅 LTP (Prev. {yesterday_date}): {price_yesterday} → {ltp}")
                print(f"   🎯 Conviction: {conviction_level} | Lot: {lot}")

                snapshot, _ = StockDailySnapshot.objects.get_or_create(
                    stock=stock,
                    date=today_date
                )
                snapshot.share_price = share_price
                snapshot.ltp = ltp
                snapshot.conviction_level = conviction_level
                snapshot.lot = lot
                snapshot.save()

                updated_ids.append(str(stock.id))

            except Exception as e:
                failed_updates.append(f"Row {idx + 2} ({company_name or 'Unknown'}): {str(e)}")

        context = {
            'upload_result': {
                'updated_ids': updated_ids,
                'skipped_names': skipped_names,
                'failed_updates': failed_updates,
                'newly_added': newly_added,
                'fallback_ids': fallback_ids,
            }
        }
        return render(request, 'UnlistedStocksUpdateSM.html', context)

    return redirect('SM_User:UnlistedStocksUpdateSM')


# custom fields
from django.shortcuts import render, get_object_or_404, redirect
from unlisted_stock_marketplace.models import *
from .forms import *

@login_required
def custom_field_list(request):
    definitions = CustomFieldDefinition.objects.select_related('stock').all()
    return render(request, 'custom_fields/definition_list.html', {'definitions': definitions})

@login_required
def custom_field_create(request):
    if request.method == 'POST':
        form = CustomFieldDefinitionForm(request.POST)
        formset = CustomFieldValueFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            definition = form.save()
            formset.instance = definition
            formset.save()
            return redirect('SM_User:custom_field_list')
    else:
        form = CustomFieldDefinitionForm()
        formset = CustomFieldValueFormSet()

    return render(request, 'custom_fields/definition_form.html', {'form': form, 'formset': formset})

@login_required
def custom_field_edit(request, pk):
    definition = get_object_or_404(CustomFieldDefinition, pk=pk)
    if request.method == 'POST':
        form = CustomFieldDefinitionForm(request.POST, instance=definition)
        formset = CustomFieldValueFormSet(request.POST, instance=definition)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('SM_User:custom_field_list')
    else:
        form = CustomFieldDefinitionForm(instance=definition)
        formset = CustomFieldValueFormSet(instance=definition)

    return render(request, 'custom_fields/definition_form.html', {'form': form, 'formset': formset})


# add broker
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Broker, Advisor
from .forms import BrokerForm, AdvisorForm  # You’ll need to create these forms

# ----------- BROKER VIEWS -----------

class BrokerListView(ListView):
    model = Broker
    template_name = 'broker/broker_list.html'
    context_object_name = 'brokers'

class BrokerCreateView(CreateView):
    model = Broker
    form_class = BrokerForm
    template_name = 'broker/broker_form.html'
    success_url = reverse_lazy('SM_User:broker-list')

class BrokerUpdateView(UpdateView):
    model = Broker
    form_class = BrokerForm
    template_name = 'broker/broker_form.html'
    success_url = reverse_lazy('SM_User:broker-list')

class BrokerDeleteView(DeleteView):
    model = Broker
    template_name = 'broker/broker_confirm_delete.html'
    success_url = reverse_lazy('SM_User:broker-list')

# ----------- ADVISOR VIEWS -----------

# views.py
class AdvisorTypeListView(ListView):
    model = Advisor
    template_name = 'advisor/advisor_type_list.html'
    context_object_name = 'types'

class AdvisorTypeCreateView(CreateView):
    model = Advisor
    fields = ['advisor_type']
    template_name = 'advisor/advisor_type_form.html'
    success_url = reverse_lazy('SM_User:advisor-type-list')

from django.views.generic import DeleteView
from django.urls import reverse_lazy

class AdvisorTypeDeleteView(DeleteView):
    model = Advisor
    template_name = 'advisor/advisor_type_confirm_delete.html'
    success_url = reverse_lazy('SM_User:advisor-type-list')



# stockData
from django.shortcuts import render, get_object_or_404, redirect
from .forms import StockDataForm
from django.db.models import Q

def stockdata_crud(request):
    search_query = request.GET.get('search', '')
    sector_filter = request.GET.get('sector', '')
    category_filter = request.GET.get('category', '')
    conviction_filter = request.GET.get('conviction_level', '')
    stock_type_filter = request.GET.get('stock_type', '')

    queryset = StockData.objects.all()

    if search_query:
        queryset = queryset.filter(
            Q(company_name__icontains=search_query) |
            Q(scrip_name__icontains=search_query) |
            Q(isin_no__icontains=search_query)
        )

    if sector_filter:
        queryset = queryset.filter(sector=sector_filter)

    if category_filter:
        queryset = queryset.filter(category=category_filter)

    if conviction_filter:
        queryset = queryset.filter(conviction_level=conviction_filter)

    if stock_type_filter:
        queryset = queryset.filter(stock_type=stock_type_filter)

    sectors = StockData.objects.values_list('sector', flat=True).distinct()
    categories = StockData.objects.values_list('category', flat=True).distinct()
    conviction_levels = StockData.objects.values_list('conviction_level', flat=True).distinct()
    stock_types = StockData.objects.values_list('stock_type', flat=True).distinct()

    form = StockDataForm()

    return render(request, 'StockDataTemplate.html', {
        'stocks': queryset,
        'form': form,
        'filters': {
            'search_query': search_query,
            'sector': sector_filter,
            'category': category_filter,
            'conviction_level': conviction_filter,
            'stock_type': stock_type_filter,
        },
        'sectors': sectors,
        'categories': categories,
        'conviction_levels': conviction_levels,
        'stock_types': stock_types,
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def edit_stockdata(request, pk):
    stock = get_object_or_404(StockData, pk=pk)
    if request.method == 'POST':
        form = StockDataForm(request.POST, request.FILES, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('SM_User:stockdata_crud')
    else:
        form = StockDataForm(instance=stock)
    return render(request, 'stockData_edit_modal.html', {'form': form, 'title': 'Edit Stock'})

