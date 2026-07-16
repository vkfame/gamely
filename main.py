import asyncio 
import os
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import get_all_rts

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

logger = logging.getLogger(__name__)

tk = os.getenv("TOKEN")
if not tk:
    raise Exception("No token provided")

bot = Bot(token=tk)
dp = Dispatcher()

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
CWD = Path.cwd()

@app.on_event("startup")
async def startup_debug():
    logger.info(f"BASE_DIR (через __file__): {BASE_DIR}")
    logger.info(f"CWD: {CWD}")
    logger.info(f"Содержимое BASE_DIR: {list(BASE_DIR.iterdir())}")

for base in [BASE_DIR, CWD]:
    for folder in ["styles", "scripts"]:
        p = base / folder
        if p.exists() and not app.routes:
            app.mount(f"/{folder}", StaticFiles(directory=str(p)), name=folder)
            break

for folder in ["styles", "scripts"]:
    p = BASE_DIR / folder
    if p.exists():
        try:
            app.mount(f"/{folder}", StaticFiles(directory=str(p)), name=folder)
        except Exception as e:
            logger.warning(f"Не удалось смонтировать {folder}: {e}")

@app.get("/")
@app.get("/index.html")
async def read_index():
    candidates = [
        BASE_DIR / "pages" / "index.html",
        BASE_DIR / "index.html",
        CWD / "pages" / "index.html",
        CWD / "index.html",
        Path("/app/pages/index.html"),
        Path("/app/index.html"),
    ]
    for path in candidates:
        logger.info(f"Проверяю: {path} — {'EXISTS' if path.exists() else 'not found'}")
        if path.exists():
            return FileResponse(str(path))

    return {"error": "index.html not found", "base_dir": str(BASE_DIR), "cwd": str(CWD)}

@app.get("/debug")
async def debug():
    import subprocess
    result = subprocess.run(["find", "/app", "-type", "f"], capture_output=True, text=True)
    return {
        "files": result.stdout.splitlines(),
        "base_dir": str(BASE_DIR),
        "cwd": str(CWD),
    }

async def on_startup(bot: Bot):
    gm = await bot.get_me()
    print(f"Робот GMLY (@{gm.username}) успешно запущен!")

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