""" emtry point for pymir-ed (pymir events dispatcher) service """

from fastapi import FastAPI


app_ed = FastAPI()

@app_ed.post('/events/taskstate')
async def root() -> str:
    return 'hello, world'
