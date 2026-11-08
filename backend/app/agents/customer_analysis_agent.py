def run(state):
    c=state['customer']
    return {'analysis':{'active_membership':bool(c['IsActiveMember']),'product_count':c['NumOfProducts'],'balance':c['Balance'],'tenure_years':c['Tenure'],'observations':['Activity is a snapshot membership flag, not transaction frequency.'],'unavailable':['transaction history','complaints','service interactions','intervention outcomes']}}
