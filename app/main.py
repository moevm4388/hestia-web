from fastapi import FastAPI


app = FastAPI()


@app.get("/functions")
async def get_functions():
    return []
