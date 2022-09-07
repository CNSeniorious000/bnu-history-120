from fastapi import FastAPI

app = FastAPI(title="BNU 120 years 🎉", description=open("readme.md", encoding="utf-8").read(), version="0.1.0")
