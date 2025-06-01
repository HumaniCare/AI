import os
import redis.asyncio as redis
import json
import subprocess
from AI.app.service.s3Service import download_from_s3
REDIS_HOST = os.getenv("REDIS_HOST", "15.165.21.152")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "babyy1023@")
CHANNEL_NAME = "spring-scheduler-channel"

async def subscribe_schedule():
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)

    print(f"Subscribed to Redis '{CHANNEL_NAME}")

    async for message in pubsub.listen():
        if message["type"] == "message":
            local_path = download_from_s3("https://humanicare-bucket.s3.ap-northeast-2.amazonaws.com/record/audio_1743069498_081a9673-aebe-4b86-a4ba-c32f4424e8b9.wav")
            subprocess.run(["mpg321", local_path])
            print("speaker out")
        