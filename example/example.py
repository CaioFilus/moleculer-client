from moleculer_client import MoleculerClient

moleculer = MoleculerClient(node_id='python-node', moleculer_nodeID="node-1", url='nats://127.0.0.1:4222')

print(moleculer.discover())
moleculer.emit('client.alive')
print(moleculer.call('microservice.action', {'data': 'moleculer test'}))
