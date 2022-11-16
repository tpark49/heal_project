from fastapi import FastAPI, HTTPException
from scheduler import scheduler
from pydantic import BaseModel


class appt(BaseModel):
    start: str 
    end: str 
    date: str

app = FastAPI()

myschedule = scheduler()

@app.get("/")
async def read_root():
   return {"hello": "world"}


@app.get("/api/appt/{date}")
async def get_appt(date): 
    response = myschedule.query_data(date)
    if response:
        return response
    raise HTTPException(404, f"There is no appt with the date {date}")

@app.get("/api/available/{date}")
async def get_appt(date): 
    response = myschedule.show_availability(date)
    if response:    
        return response
    raise HTTPException(404, f"There is no available appt with the date {date}")


@app.post("/api/schedule")
async def add_appt(appt:appt):
    response = myschedule.schedule_appt(appt.start, appt.end, appt.date)
    if response:
        return "Successfully added appt"
    raise HTTPException(400, "Something went wrong")


@app.delete("/api/appt/")
async def delete_todo(appt:appt):
    response = myschedule.remove_appt(appt.start, appt.end, appt.date)
    if response:
        return "Successfully deleted appt"
    raise HTTPException(404, "There is no appt with given information")


@app.put("/api/appt/")
async def put_todo(start:str, end:str, date: str, new_start:str, new_end:str, new_date:str):
    response = myschedule.update_appt(start, end, date, new_start, new_end, new_date) 
    if response:
        return "Successfully updated appt"
    raise HTTPException(404, "There was an issue with update")
