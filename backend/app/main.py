from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.tickets import router as tickets_router

app = FastAPI(title="AI Ticket Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册工单路由
app.include_router(tickets_router)

@app.get("/")
def root():
    return {"message": "AI Ticket Agent is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}