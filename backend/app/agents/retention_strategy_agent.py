def run(state):
    c=state['customer']; p=state['prediction']; strategies=[]
    if not c['IsActiveMember']:
        strategies.append({'strategy':'Offer digital banking assistance','reason':'Inactive membership flag in supplied snapshot','evidence':{'IsActiveMember':0},'action':'Ask whether the customer would welcome help using existing services.'})
    if c['NumOfProducts']==1:
        strategies.append({'strategy':'Offer an optional service review','reason':'One recorded banking product','evidence':{'NumOfProducts':1},'action':'Review current needs; check suitability before discussing any product.'})
    if not strategies:
        strategies.append({'strategy':'Schedule a relationship check-in','reason':'Review model assessment with customer context','evidence':{'risk':p['risk']},'action':'Invite voluntary feedback; validate needs before proposing an action.'})
    for s in strategies:
        s.update(priority=p['risk'],estimated_retention_impact=None,expected_outcome='Understand needs and support engagement; retention effect unmeasured',assumptions=['No complaint or transaction evidence available'],requires_human_review=True)
    return {'strategies':strategies}
