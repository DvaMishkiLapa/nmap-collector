import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime

from sanic import Sanic
from sanic.config import Config
# from sanic.blueprints import Blueprint
# from sanic.exceptions import NotFound
# from sanic.log import logger
from sanic.response import json
from sanic_ext import validate
from sanic_motor import BaseModel

from nmap_xml_parser import NmapXmlInfo

# from sanic_openapi import doc, openapi3_blueprint

Config.RESPONSE_TIMEOUT = 240
Config.REQUEST_TIMEOUT = 240

app = Sanic(__name__)
# app.blueprint(openapi3_blueprint)

mongo_uri = "mongodb://{host}:{port}/{database}".format(
    database='nmap',
    port=27017,
    host='mongodb'
)

app.config.update(dict(MOTOR_URI=mongo_uri))

BaseModel.init_app(app)

xml_folder = 'xmls'


class Collector(BaseModel):
    __coll__ = "collector"


def serialz_id(objs: list) -> list:
    for x in objs:
        x['_id'] = str(x['_id'])
    return objs


def nmap_scan(host: str, save_xml: bool = False) -> str:
    nmap_cmd_template = f'nmap {host} -T4 -sV -O -p- -min-parallelism 100 --min-rate 64 -oX'
    if save_xml:
        now_datatime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
        xml_path = f'{xml_folder}/{now_datatime}_{host}.xml'
        nmap_cmd = f'{nmap_cmd_template} {xml_path}'
        subprocess.call(shlex.split(nmap_cmd))
        return xml_path
    nmap_cmd = f'{nmap_cmd_template} -'
    result = subprocess.Popen(shlex.split(nmap_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return result[0].decode('utf-8')


@dataclass
class NmapParams:
    host: str
    save_xml: bool


@app.post("/scan")
@validate(json=NmapParams)
async def scan(request, body: NmapParams):
    args = request.json
    scan_result = nmap_scan(args['host'], args['save_xml'])
    scan_parse = NmapXmlInfo(scan_result, args['save_xml']).info
    update_result = await Collector.insert_many(scan_parse)
    return json({
        'data': serialz_id(scan_parse),
        'objectIds': [str(x) for x in update_result.inserted_ids],
    }, 200)

app.run(host="0.0.0.0", port=8000, debug=True)
