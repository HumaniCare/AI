import time

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app="app.service.main:app",
        host="localhost",
        # host="0.0.0.0",
        port=8000,
    )