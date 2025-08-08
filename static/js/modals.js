document.addEventListener('DOMContentLoaded', () => {
  const brokers = JSON.parse(document.getElementById('brokers-data').textContent);
  const advisors = JSON.parse(document.getElementById('advisors-data').textContent);

  function populateSelect(selectId, items) {
    const select = document.getElementById(selectId);
    select.innerHTML = '';
    items.forEach(item => {
      const option = document.createElement('option');
      option.value = item.id;
      option.text = item.name || item.advisor_type || 'Unnamed';
      select.appendChild(option);
    });
  }

  window.openBuyModal = function (el) {
    document.getElementById('buy-stock-id').value = el.dataset.stockId;
    document.getElementById('buy-stock-name').innerText = el.dataset.companyName;
    document.getElementById('buy-share-price').innerText = `₹${el.dataset.sharePrice}`;
    document.getElementById('buy-quantity').value = el.dataset.lot;
    document.getElementById('buy-price-per-share').value = el.dataset.sharePrice;
    populateSelect('buy-advisor', advisors);
    populateSelect('buy-broker', brokers);
    document.getElementById('buy-form').action = `/buy_stock/${el.dataset.stockId}/`;
    $('#universalBuyModal').modal('show');
  };

  window.openSellModal = function (el) {
    document.getElementById('sell-stock-id').value = el.dataset.stockId;
    document.getElementById('sell-stock-name').innerText = el.dataset.companyName;
    document.getElementById('sell-stock-lot').innerText = `Qty: ${el.dataset.lot}`;
    document.getElementById('sell-quantity').value = el.dataset.lot;
    populateSelect('sell-advisor', advisors);
    populateSelect('sell-broker', brokers);
    document.getElementById('sell-form').action = `/sell_stock/${el.dataset.stockId}/`;
    $('#universalSellModal').modal('show');
  };
});
