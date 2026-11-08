import pandas as pd
from ..ml.predict import artifact
from ..ml.segmentation import SEGMENT_FEATURES
def run(state):
    a=artifact()['segmentation']; x=pd.DataFrame([state['customer']])[SEGMENT_FEATURES]
    label=int(a['model'].predict(a['scaler'].transform(x))[0])
    return {'segment':{**a['profiles'][label],'silhouette':a['silhouette'],'note':'Account profile grouping; balance is not total customer value'}}
