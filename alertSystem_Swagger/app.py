import requests
import json
from flask import Flask, jsonify
import connexion
app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger.yml')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
