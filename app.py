from flask import Flask, render_template, jsonify, request, abort, make_response
from pymongo import *
from bson import ObjectId

app = Flask(__name__, static_url_path="")
client = MongoClient("localhost", 27017)
db = client.dbjungle


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/memo", methods=["GET"])
def get_memo():
    result = list(db.memos.find({}).sort("likes", DESCENDING))

    # ObjectId를 문자열로 변환
    # ObjectId를 바로 json으로 바꿀수 없기 때문에 문자열로 변환함. 모든 메모에 대해서 변환해야 함.
    for i in range(len(result)):
        result[i]["_id"] = str(result[i]["_id"])

    return jsonify(result)


@app.route("/api/memo", methods=["POST"])
def create_memo():
    json = request.json

    if "title" not in json or "text" not in json:
        abort(400)

    title = json["title"]
    text = json["text"]

    memo = {"title": title, "text": text, "likes": 0}

    id = db.memos.insert_one(memo).inserted_id

    return jsonify({"_id": str(id)})


@app.route("/api/memo", methods=["PUT"])
def edit_memo():
    json = request.json

    if "_id" not in json or "title" not in json or "text" not in json:
        abort(400)

    id = json["_id"]
    title = json["title"]
    text = json["text"]

    query_filter = {"_id": ObjectId(id)}
    update_operation = {"$set": {"title": title, "text": text}}
    result = db.memos.update_one(query_filter, update_operation)

    if result.matched_count == 1:
        return make_response("")
    else:
        return make_response("id not exist", 404)


@app.route("/api/memo", methods=["DELETE"])
def delete_memo():
    json = request.json

    if "_id" not in json:
        abort(400)

    id = json["_id"]

    query_filter = {"_id": ObjectId(id)}
    result = db.memos.delete_one(query_filter)

    if result.deleted_count == 1:
        return make_response("")
    else:
        return make_response("id not exist", 404)


@app.route("/api/memo/increase_like", methods=["POST"])
def increase_likes():
    json = request.json

    if "_id" not in json:
        abort(400)

    id = json["_id"]

    query_filter = {"_id": ObjectId(id)}
    update_operation = {"$inc": {"likes": 1}}
    result = db.memos.update_one(query_filter, update_operation)

    if result.matched_count == 1:
        return make_response("")
    else:
        return make_response("id not exist", 404)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001, debug=True)
