import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import wifi

app = FastAPI(title="WiFi Scan & Jammer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wifi.router, prefix="/api/wifi", tags=["wifi"])

@app.get("/")
def root():
    return {"message": "WiFi Scan & Jammer API"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)