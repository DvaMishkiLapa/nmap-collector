import os
import shlex
import subprocess

from sanic import Sanic
from sanic.config import Config
# from sanic.blueprints import Blueprint
# from sanic.exceptions import NotFound
# from sanic.log import logger
from sanic.response import json
from sanic_motor import BaseModel

from nmap_xml_parser import NmapXmlInfo

# from sanic_openapi import doc, openapi3_blueprint

Config.RESPONSE_TIMEOUT = 120
Config.REQUEST_TIMEOUT = 120

app = Sanic(__name__)
# app.blueprint(openapi3_blueprint)

mongo_uri = "mongodb://{host}:{port}/{database}".format(
    database='nmap',
    port=27017,
    host='mongodb'
)

settings = dict(
    MOTOR_URI=mongo_uri,
    LOGO=None,
)
app.config.update(settings)

BaseModel.init_app(app)

xml_folder = 'xmls'
nmap_cmd = f'nmap -sV -O -p- localhost -oX {xml_folder}/scan.xml'
nmap_args = shlex.split(nmap_cmd)


class Collector(BaseModel):
    __coll__ = "collector"


def serialz_id(objs: list) -> list:
    for x in objs:
        x['_id'] = str(x['_id'])
    return objs


@app.get("/scan")
async def scan(request):
    result = subprocess.call(nmap_args)
    scan_result = NmapXmlInfo(f'{xml_folder}/scan.xml', True).info
    update_result = await Collector.insert_many(scan_result)
    return json({
        'data': serialz_id(scan_result),
        'objectIds': [str(x) for x in update_result.inserted_ids],
        'subprocess_status': result
    }, 200)

app.run(host="0.0.0.0", port=8000, debug=1)
