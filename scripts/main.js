const tg = window.Telegram.WebApp;

tg.expand();

const user = tg.initDataUnsafe?.user;
const userDisplay = document.getElementById('user-display');

if (user) {
    const username = user.username ? `@${user.username}` : user.first_name;
    userDisplay.textContent = `Игрок: ${username}`;
} else {
    userDisplay.textContent = `Запущено вне Telegram`;
}

function startGame(gameName) {
    if (tg.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('medium');
    }
    
    tg.showAlert(`Запуск игры "${gameName}"\n\nРаздел находится в разработке.`);
}