const webAppUrl = "{{ web_app_url }}"
const tg = window.Telegram?.WebApp;
const initData = tg.initData;

fetch(`${webAppUrl}/validate`, {
    method: 'POST',
    headers: {
        'Authorization': `tma ${initData}`,
        'Content-Type': 'application/json',
    },
    credentials: 'include',
})
.then(response => {
    if (!response.ok) {
        throw new Error('Ошибка при валидации');
    }
    return response.json();
})
.then(data => {
    console.log(data)
})
.catch(error => {
    console.error('Ошибка:', error);
});
