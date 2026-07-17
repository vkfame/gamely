import asyncio
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import get_all_rts

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tk = os.getenv("TOKEN")
if not tk:
    raise Exception("No token provided")

bot = Bot(token=tk)
dp = Dispatcher()

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"BASE_DIR: {BASE_DIR}")
    logger.info(f"APP_DIR exists: {APP_DIR.exists()}")
    if APP_DIR.exists():
        logger.info(f"Содержимое app/: {list(APP_DIR.iterdir())}")
    yield

app = FastAPI(lifespan=lifespan)

# Монтируем всю папку app/ как статику
if APP_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(APP_DIR)), name="app")
    logger.info("Смонтировано /app")

@app.get("/")
@app.get("/index.html")
async def read_index():
    candidates = [
        APP_DIR / "index.html",
        BASE_DIR / "index.html",
        Path("/app/index.html"),  # на случай если BASE_DIR == /app
    ]
    for path in candidates:
        logger.info(f"Проверяю: {path} — {'EXISTS' if path.exists() else 'not found'}")
        if path.exists():
            return FileResponse(str(path))

    return {
        "error": "index.html not found",
        "base_dir": str(BASE_DIR),
        "app_dir": str(APP_DIR),
        "app_dir_exists": APP_DIR.exists(),
    }

@app.get("/debug")
async def debug():
    import subprocess
    result = subprocess.run(["find", "/", "-name", "index.html", "-type", "f"], capture_output=True, text=True)
    return {
        "index_html_locations": result.stdout.splitlines(),
        "base_dir": str(BASE_DIR),
        "app_dir": str(APP_DIR),
        "cwd": str(Path.cwd()),
    }

async def on_startup(bot: Bot):
    gm = await bot.get_me()
    logger.info(f"Робот GMLY (@{gm.username}) успешно запущен!")

async def main():
    dp.startup.register(on_startup)
    dp.include_router(get_all_rts())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")