from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from pysnmp.hlapi import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'

#Initialize the database
db = SQLAlchemy(app)

#Create database model
class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    ip = db.Column(db.String(200), nullable=False)
    marque = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id

class AddClient(Resource):

    def post(self, client, ip, marque):
        new_client = Clients(name=client, ip=ip, marque=marque)

        #Push to Database
        try:
            db.session.add(new_client)
            db.session.commit()
            return 'Client was successfuly added !'
        except:
            return "There was an error adding your client."

class ShowClients(Resource):

    def get(self):
        res = {}
        clients = Clients.query.all()
        #cpt = 0
        for cl in clients:
            print(cl.name+' '+cl.ip+' '+cl.marque)
            res[cl.id] = cl.name
            #cpt = cpt + 1
        return res

class DeleteClient(Resource):
    def delete(self, id):
        Clients.query.filter(Clients.id == id).delete()
        db.session.commit()
        return 'Delete done !'

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
api.add_resource(AddClient, '/addclient/<string:client>/<string:ip>/<string:marque>')
api.add_resource(ShowClients, '/showclients')
api.add_resource(DeleteClient, '/deleteclient/<int:id>')

if __name__ == "__main__":
    app.run()