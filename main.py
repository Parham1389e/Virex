import asyncio
import logging
from bot.app import build_application

async def run():
    app = build_application(); await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
    try: await asyncio.Event().wait()
    finally: await app.updater.stop(); await app.stop(); await app.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); asyncio.run(run())
