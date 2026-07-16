from aiogram import Bot, Dispatcher
import asyncio 
import os
from dotenv import load_dotenv
from handlers import get_all_rts

load_dotenv()

tk = os.getenv("TOKEN")
if not tk:
    raise Exception("No token provided")

bot = Bot(token=tk)
dp = Dispatcher()

async def on_startup():
    gm = await bot.get_me()
    print(f"Bot {gm.id} started")

async def main():
    await dp.startup.register(on_startup)

    await dp.include_router(get_all_rts())
    await dp.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        print(e)