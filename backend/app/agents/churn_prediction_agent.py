from ..ml.predict import predict
def run(state): return {'prediction':predict(state['customer'])}
