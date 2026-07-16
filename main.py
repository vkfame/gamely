from aiogram import Bot, Dispatcher
import asyncio 
import os
from dotenv import load_dotenv
from handlers import get_all_rts
from fastapi import FastAPI
import uvicorn

load_dotenv()

tk = os.getenv("TOKEN")
if not tk:
    raise Exception("No token provided")

bot = Bot(token=tk)
dp = Dispatcher()
app = FastAPI()

async def on_startup():
    gm = await bot.get_me()
    print(f"Bot {gm.id} started")

async def main():
    await dp.startup.register(on_startup)

    await dp.include_router(get_all_rts())
    await dp.start_polling()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        print(e)