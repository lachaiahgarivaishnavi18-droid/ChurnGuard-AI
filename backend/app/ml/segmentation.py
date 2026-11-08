from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

SEGMENT_FEATURES=['Balance','Tenure','NumOfProducts','IsActiveMember']

def train_segments(X):
    scale=make_pipeline(SimpleImputer(strategy='median'),StandardScaler())
    values=scale.fit_transform(X[SEGMENT_FEATURES])
    candidates=[]
    for k in range(2,6):
        model=KMeans(k,n_init=10,random_state=42).fit(values)
        score=silhouette_score(values,model.labels_,sample_size=min(1200,len(X)),random_state=42)
        candidates.append((score,model))
    score,model=max(candidates,key=lambda v:v[0])
    profiles=[]
    for i in range(model.n_clusters):
        group=X.loc[model.labels_==i,SEGMENT_FEATURES]
        means=group.mean().to_dict()
        label=('Inactive' if means['IsActiveMember']<.5 else 'Active')+' · '+('higher balance' if means['Balance']>X.Balance.median() else 'lower balance')
        profiles.append({'id':i,'name':label,'means':means,'count':len(group)})
    return {'scaler':scale,'model':model,'silhouette':float(score),'profiles':profiles}
