from django.shortcuts import render

def BlogSM(request):
    return render(request, 'BlogSM.html')

# views.py

from django.shortcuts import render, redirect
from .models import HeroSectionBanner
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from .models import *
from unlisted_stock_marketplace.models import *

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

def UnlistedStocksUpdateSM(request):
    today = timezone.now().date()

    if request.method == "POST":
        stock_id = request.POST.get('stock_id')
        share_price_str = request.POST.get('share_price')
        conviction_level = request.POST.get('conviction_level')
        lot_size_str = request.POST.get('lot_size')

        if stock_id:
            stock = get_object_or_404(StockData, pk=stock_id)

            try:
                share_price = Decimal(share_price_str) if share_price_str else None
            except (InvalidOperation, TypeError):
                share_price = None

            try:
                lot_size = int(lot_size_str) if lot_size_str else None
            except (ValueError, TypeError):
                lot_size = None

            if lot_size is not None:
                stock.lot = lot_size
            if conviction_level:
                stock.conviction_level = conviction_level
            stock.save()

            snapshot, _ = StockDailySnapshot.objects.get_or_create(stock=stock, date=today)

            if share_price is not None:
                snapshot.share_price = share_price
            if conviction_level:
                snapshot.conviction_level = conviction_level
            snapshot.save()

            return redirect('SM_User:UnlistedStocksUpdateSM')

    query = request.GET.get('q', '')
    all_stocks = StockData.objects.all()

    if query:
        all_stocks = all_stocks.filter(Q(company_name__icontains=query) | Q(sector__icontains=query))

    snapshots = []
    for stock in all_stocks:
        today_snapshot = StockDailySnapshot.objects.filter(stock=stock, date=today).first()
        if today_snapshot:
            snapshots.append(today_snapshot)
        else:
            latest_snapshot = StockDailySnapshot.objects.filter(stock=stock).order_by('-date').first()
            snapshots.append(latest_snapshot or StockDailySnapshot(stock=stock, date=today))

    return render(request, 'UnlistedStocksUpdateSM.html', {
        'snapshots': snapshots,
        'conviction_choices': CONVICTION_CHOICES,
        'search_query': query,
        'today': today,
    })

def download_unlisted_stocks_csv(request):
    today = timezone.now().date()
    snapshot_qs = StockDailySnapshot.objects.filter(date=today).select_related('stock')

    unique_stock_ids = set()
    filtered_snapshots = []
    for snapshot in snapshot_qs:
        if snapshot.stock.id not in unique_stock_ids:
            unique_stock_ids.add(snapshot.stock.id)
            filtered_snapshots.append(snapshot)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="unlisted_stocks_update.csv"'

    writer = csv.writer(response)
    writer.writerow(['Company Name', 'Conviction Level', 'Share Price'])

    for snapshot in filtered_snapshots:
        writer.writerow([snapshot.stock.company_name, snapshot.conviction_level, snapshot.share_price])

    return response

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


