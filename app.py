from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from pysnmp.hlapi import *

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Informations(Resource):
    def get(self, ipaddress, oid, community):

        iterator = getCmd(SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ipaddress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)))

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:  # SNMP engine errors
            print(errorIndication)
        else:
            if errorStatus:  # SNMP agent errors
                print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex)-1] if errorIndex else '?'))
            else:
                for varBind in varBinds:  # SNMP response contents
                    print(' = '.join([x.prettyPrint() for x in varBind]))
                    res = [x.prettyPrint() for x in varBind]
        return {res[0]: res[1]}

api.add_resource(HelloWorld, '/')
api.add_resource(Informations, '/informations/<string:ipaddress>/<string:oid>/<string:community>')

if __name__ == "__main__":
    app.run()