from dbconf import cnxpool

import os,sys,shutil,datetime

from fastapi import *
from fastapi.responses import FileResponse,JSONResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware

# initialize FastAPI app 
app=FastAPI()

# 設定 uploads folder
os.makedirs("uploads", exist_ok=True)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在AWS部署後，改成指定網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


required_vars = [
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_NAME",
]
# Check for missing environment variables
missing = [var for var in required_vars if os.getenv(var) is None]

if missing:
    print("Missing required environment variables:")
    for var in missing:
        print(f" - {var}")
    print("Please make sure your .env file is configured correctly.")
    sys.exit(1)



templates=Jinja2Templates(directory="static")

# Static Pages
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")


# 建立新的留言內容 API
@app.post("/api/messages")
async def post_message(
    comment: str = Form(...),
    image: UploadFile = File(...),
    request: Request = None
):
    try:
        # 儲存圖片到本機
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        file_path = os.path.join("uploads", filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_url = f"/uploads/{filename}"  # 之後可以改成 AWS S3 的網址

        # 將留言、圖片網址、時間戳記 insert 進 db
        with cnxpool.get_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO msgboard (comment, image_url, created_at)
                    VALUES (%s, %s, %s)
                    """,
                    [comment, image_url, datetime.datetime.now()]
                )
                cnx.commit()

        return JSONResponse(status_code=200, content={"ok": True, "image_url": image_url})

    except Exception as e:
        print("錯誤訊息：", e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )


# 取得留言內容 API
@app.get("/api/messages")
async def get_messages(request: Request):
    try:
        with cnxpool.get_connection() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id, comment, image_url, created_at
                    FROM msgboard
                    ORDER BY created_at DESC
                    LIMIT 20
                """)
                results = cursor.fetchall()

                # 設定回傳給前端的資料格式
                messages = []
                for row in results:
                    messages.append({
                        "id": row["id"],
                        "comment": row["comment"],
                        "image_url": row["image_url"],
                        "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    })

        return JSONResponse(status_code=200, content={"ok": True, "messages": messages})

    except Exception as e:
        print("錯誤訊息：", e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )



app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads") # 之後改用 S3 儲存圖片後，圖片就從 S3 URL載入，不需要在後端這裡處理 /uploads



# app.mount("/",StaticFiles(directory="static",html=True))
# app.mount("/static", StaticFiles(directory="static"), name="static")