import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import MongoDB
from config.development import config
from model.student import createStudentModel, updateStudentModel

mongo_config = config["mongo_config"]
mongo_db = MongoDB(  # เรียกใช้MongoDBเเละส่งค่า
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()  # mongodb

app = FastAPI()

app.add_middleware(  # ตัวคั่นกลาง
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#    C      R       U           D
# [ post , gat,[put,patch] , delete ]


@app.get("/")
def index():
    return JSONResponse(content={"message": "Student Info"}, status_code=200)


@app.get("/students/")
def get_students(
    sort_by: Optional[str] = None,  # ถ้าค่าไม่เป็นstrให้เป็นnone
    order: Optional[str] = Query(None, min_length=3, max_length=4),
):

    try:
        result = mongo_db.find(sort_by, order)  # .fild,mongodb
    except:  # ต่อไม่ได้ไปraise
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/students/{student_id}")  # ค่าที่ส่งต้องมีminและmax10
def get_students_by_id(student_id: str = Path(None, min_length=10, max_length=10)):
    try:
        result = mongo_db.find_one(student_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")
    # apiเซิฟerror
    if result is None:
        raise HTTPException(status_code=404, detail="Student Id not found !!")
    # ค่าที่ส่งไม่มีdatabase
    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/students")
def create_books(student: createStudentModel):  # clss,studen
    try:  # กันเกิดปัญหา
        student_id = mongo_db.create(student)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": student_id,
            },
        },
        status_code=201,  # 201insert
    )


@app.patch("/students/{student_id}")  # update
def update_books(
    student: updateStudentModel,  # clss
    student_id: str = Path(None, min_length=10, max_length=10),
):  # เข้าระบบ
    print("student", student)
    try:  # def update
        updated_student_id, modified_count = mongo_db.update(student_id, student)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:  # modified_countจำนวนค่าที่เปลียน
        raise HTTPException(
            status_code=404,
            detail=f"Student Id: {updated_student_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": updated_student_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/students/{student_id}")
def delete_book_by_id(student_id: str = Path(None, min_length=10, max_length=10)):
    try:
        deleted_student_id, deleted_count = mongo_db.delete(student_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Student Id: {deleted_student_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": deleted_student_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
