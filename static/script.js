// script.js (acciones comunes)
document.addEventListener('DOMContentLoaded', function(){
  // conversor XE: abrir en nueva pestaña
  const elXE = document.getElementById('convXE');
  if (elXE) elXE.addEventListener('click', () => window.open('https://www.xe.com/es-es/currencyconverter/', '_blank'));

  // conversor manual: pedir cantidad, usar API exchangerate.host para tasa
  const elManual = document.getElementById('convManual');
  if (elManual) elManual.addEventListener('click', async () => {
    let amount = prompt('Cantidad en €:');
    if (amount === null) return;
    amount = parseFloat(amount.replace(',', '.'));
    if (isNaN(amount)) { alert('Cantidad inválida'); return; }
    try {
      const r = await fetch('https://api.exchangerate.host/latest?base=EUR&symbols=USD');
      const j = await r.json();
      const rate = j.rates && j.rates.USD ? j.rates.USD : 1.07;
      const res = amount * rate;
      alert(`€${amount.toFixed(2)} = $${res.toFixed(2)} USDT\n(Tasa: ${rate.toFixed(4)})`);
      try { navigator.clipboard.writeText(`${res.toFixed(2)} USDT`); } catch(e){}
    } catch (err) {
      alert('No se pudo obtener la tasa online. Intenta de nuevo.');
    }
  });
});
