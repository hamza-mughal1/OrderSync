from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from main import Database
import json

db_config = json.load(open("config.json"))

mydb = Database(
    host=db_config["host"],
    user=db_config["user"],
    password=db_config["password"],
    database=db_config["database"],
)

parser = reqparse.RequestParser()
parser.add_argument("data")
app = Flask("OrderSync")
api = Api(app)


class OrderSync(Resource):
    def get(self, data_specs):
        if data_specs == "all_products":
            re = mydb.all_products()
            return re[1], re[0]
        elif data_specs == "all_sales":
            re = mydb.all_sales()
            return re[1], re[0]

    def put(self, data_specs):
        print(data_specs)
        args = parser.parse_args()
        args = dict(args)
        json_str = args["data"].replace("'", '"')
        json_dict = json.loads(json_str)
        mydb.place_order(json_dict)


api.add_resource(OrderSync, "/data/<data_specs>")

if __name__ == "__main__":
    app.run(debug=True)
