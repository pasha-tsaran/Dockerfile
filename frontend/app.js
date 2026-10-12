const form = document.querySelector('#calculator');
const button = document.querySelector('#submit');
const errorBox = document.querySelector('#error');
const result = document.querySelector('#result');
const expression = document.querySelector('#expression');
const responseBox = document.querySelector('#response');
const statusBox = document.querySelector('#status');
const hostname = document.querySelector('#hostname');

async function checkHealth() {
  try {
    const response = await fetch('/api/health', { cache: 'no-store', signal: AbortSignal.timeout(5000) });
    if (!response.ok) throw new Error('Бэкенд недоступен');
    const data = await response.json();
    if (data.status !== 'ok') throw new Error('Бэкенд недоступен');
    statusBox.textContent = '● Flask доступен';
    statusBox.classList.remove('offline');
    hostname.textContent = `Имя хоста: ${data.hostname}`;
  } catch {
    statusBox.textContent = '● Нет соединения с Flask';
    statusBox.classList.add('offline');
    hostname.textContent = '';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  result.textContent = '—';
  responseBox.textContent = 'Выполняем запрос…';
  expression.textContent = 'Вычисляем…';
  button.disabled = true;
  try {
    const a = document.querySelector('#a').valueAsNumber;
    const b = document.querySelector('#b').valueAsNumber;
    const operation = document.querySelector('#operation').value;
    if (!Number.isFinite(a) || !Number.isFinite(b)) throw new Error('Введите два конечных числа.');
    const response = await fetch('/api/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a, b, operation }),
      signal: AbortSignal.timeout(15000),
    });
    if (!response.headers.get('content-type')?.includes('application/json')) {
      throw new Error('Бэкенд недоступен. Попробуйте ещё раз.');
    }
    const data = await response.json();
    responseBox.textContent = JSON.stringify(data, null, 2);
    if (!response.ok) throw new Error(data.error || 'Ошибка вычисления.');
    result.textContent = String(data.result);
    expression.textContent = `${data.a} ${data.operation === 'add' ? '+' : '−'} ${data.b} = ${data.result}`;
  } catch (error) {
    errorBox.textContent = error.name === 'TimeoutError' || error instanceof TypeError
      ? 'Не удалось получить ответ. Проверьте соединение и повторите запрос.' : error.message;
    errorBox.hidden = false;
    expression.textContent = 'Вычисление не выполнено.';
    if (responseBox.textContent === 'Выполняем запрос…') responseBox.textContent = 'Ответ не получен.';
  } finally {
    button.disabled = false;
    checkHealth();
  }
});

checkHealth();
setInterval(checkHealth, 10000);
