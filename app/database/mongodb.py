import pymongo

from model.student import createStudentModel, updateStudentModel


class MongoDB:
    def __init__(self, host, port, user, password, auth_db, db, collection):
        self.host = host  # กำหนดตัวเเปร
        self.port = port
        self.user = user
        self.password = password
        self.auth_db = auth_db
        self.db = db
        self.collection = collection
        self.connection = None

    def _connect(self):  # ต่อclient
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            authSource=self.auth_db,
            authMechanism="SCRAM-SHA-1",
        )
        db = client[self.db]  # ต่อกับค่าdbในconfig
        self.connection = db[self.collection]  # ต่อกับค่าcollection

    def find(self, sort_by, order):
        mongo_results = self.connection.find({})
        if sort_by is not None and order is not None:  # เชคไม่เป็นค่าว่าง
            mongo_results.sort(sort_by, self._get_sort_by(order))  # เรียงน้อยไปมาก

        return list(mongo_results)

    def _get_sort_by(self, sort: str) -> int:
        return pymongo.DESCENDING if sort == "desc" else pymongo.ASCENDING  # มากไปน้อย

    def find_one(self, id):
        return self.connection.find_one({"_id": id})  # .find_oneเอามาidเดียว

    def create(self, student: createStudentModel):
        student_dict = student.dict(exclude_unset=True)  # แปลงค่าเป็นjson
        #   student_dict["_id"] = student_dict["id"]
        #   insert_dict = student_dict  ได้ addressเดิม
        insert_dict = {**student_dict, "_id": student_dict["id"]}
        # **ได้addressใหม่ตลอดเวลา
        inserted_result = self.connection.insert_one(insert_dict)
        student_id = str(inserted_result.inserted_id)
        # inserted_id resuleทีreturnจากinsert_one

        return student_id

    def update(self, student_id, student: updateStudentModel):  # รับstudent_id, student
        updated_result = self.connection.update_one(
            {"id": student_id}, {"$set": student.dict(exclude_unset=True)}  # แปลงdict
        )
        return [student_id, updated_result.modified_count]
        # modified_countค่าที่เปลียนเเปลง

    def delete(self, student_id):
        deleted_result = self.connection.delete_one({"id": student_id})  # .delete_one
        return [student_id, deleted_result.deleted_count]
