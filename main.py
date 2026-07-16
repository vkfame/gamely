import asyncio 
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import get_all_rts

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

load_dotenv()

tk = os.getenv("TOKEN")
if not tk:
    raise Exception("No token provided")

bot = Bot(token=tk)
dp = Dispatcher()
app = FastAPI()

current_dir = os.path.dirname(os.path.realpath(__file__))

styles_path = os.path.join(current_dir, "styles")
scripts_path = os.path.join(current_dir, "scripts")

if os.path.exists(styles_path):
    app.mount("/styles", StaticFiles(directory=styles_path), name="styles")
if os.path.exists(scripts_path):
    app.mount("/scripts", StaticFiles(directory=scripts_path), name="scripts")

@app.get("/")
async def read_index():
    index_path = os.path.join(current_dir, "pages", "index.html")
    
    if not os.path.exists(index_path):
        print(f"Error: File not found at path {index_path}")
        return {"error": "Index.html not found on server"}, 404
        
    return FileResponse(index_path)

async def on_startup(bot: Bot):
    gm = await bot.get_me()
    print(f"Bot @{gm.username} (ID: {gm.id}) sucessfully started!")

async def start_all():
    dp.startup.register(on_startup)
    dp.include_router(get_all_rts())

    config = uvicorn.Config(app, host="0.0.0.0", port=3000, log_level="info")
    server = uvicorn.Server(config)

    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )

if __name__ == "__main__":
    try:
        asyncio.run(start_all())
    except KeyboardInterrupt:
        print("Приложение остановлено пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")