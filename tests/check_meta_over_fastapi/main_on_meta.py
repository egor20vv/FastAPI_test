from fastapi import FastAPI, status
import uvicorn
import meta_schemas

app = FastAPI()


@app.post('/',
          # response_model=meta_schemas.BaseSchema.Create,
          status_code=status.HTTP_201_CREATED)
def try_post(some_data: meta_schemas.BaseSchema.Edit):
    print(some_data)
    return None


if __name__ == '__main__':
    uvicorn.run("main_on_meta:app", port=5000, reload=True, access_log=False)