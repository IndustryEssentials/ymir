""" emtry point for pymir-ed (pymir events dispatcher) service """

from fastapi import FastAPI
from pydantic import BaseModel


class TaskStatesEvent(BaseModel):
    pass


app_ed = FastAPI()

@app_ed.post('/events/taskstate')
async def root(tse: TaskStatesEvent) -> str:
    return 'hello, world'
