# https://fastapi.tiangolo.com/tutorial/request-files/
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse

from transcripts.custom_types import Product, ProductsResponse
from transcripts.infer_products import infer_products, infer_youtube
from transcripts.io import files_to_textchunks

app = FastAPI()


@app.post("/products/", response_model=ProductsResponse)
async def products(files: list[UploadFile]) -> ProductsResponse:
    texts = files_to_textchunks(files=files)
    return ProductsResponse(products=infer_products(texts=texts))


@app.post("/product/youtube/", response_model=Product)
async def youtube(files: list[UploadFile]) -> Product:
    texts = files_to_textchunks(files=files)
    return infer_youtube(texts=texts)


@app.get("/")
async def main():
    content = """
<body>
<h3>Infer Products</h3>
<form action="/products/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple accept=".pdf">
<input type="submit">
</form>

<h3>Summarize YouTube</h3>
<form action="/product/youtube/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple accept=".pdf">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
