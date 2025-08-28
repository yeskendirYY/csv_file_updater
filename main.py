from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from tasks.file_update import file_update
from pathlib import Path
from celery_app import celery_app, update_files_task

class EmitentData(BaseModel):
    emitent_id: str
    ticker: str

app = FastAPI()


CURRENT_DIR = Path(__file__).parent
# CSV_FILE = CURRENT_DIR / "data" / f"{ticker.lower()}.csv"



@app.get("/health")
def health_check():
    try:
        stats = celery_app.control.inspect().stats()
        if stats:
            return {"status": "healthy", "celery_workers": len(stats)}
        else:
            return {"status": "unhealthy", "error": "No Celery workers available"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}



@app.post("/get_file")
async def get_csv_file(emitent: EmitentData): 
    CSV_FILE = CURRENT_DIR / "data" / f"{emitent.ticker.lower()}.csv"
    try:
        with open(CSV_FILE, "rb") as file:
            file_content = file.read()
        return Response(
            content = file_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")