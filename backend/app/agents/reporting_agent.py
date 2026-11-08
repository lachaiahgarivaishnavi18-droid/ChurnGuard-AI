import os, requests
from ..schemas import Narrative

def run(state):
    p=state['prediction']; e=state['explanation']
    if p['model_version']!=e['model_version'] or abs(e['reconstructed_probability']-p['probability'])>.005:
        raise ValueError('Explanation does not reconcile with prediction')
    report={k:state[k] for k in ['analysis','prediction','explanation','segment','strategies']}
    report['limitations']=['Snapshot associations are not causes.','Estimated retention impact is unavailable without controlled intervention evidence.','Training records may appear in customer demo; held-out evaluation is in model metrics.','Human review required; no outreach or account action is performed.']
    report['narrative_mode']='deterministic evidence report'
    key=os.getenv('LLM_API_KEY')
    if key:
        # An optional LLM receives only grounded aggregate evidence, never identifiers.
        payload={'model':os.getenv('LLM_MODEL','gpt-4.1-mini'),'messages':[{'role':'system','content':'Summarize the supplied evidence only. Do not infer dissatisfaction or causes, invent numbers, or propose credit or financial incentives. Return JSON with summary and questions_for_analyst.'},{'role':'user','content':str({'risk':p['risk'],'segment':state['segment']['name'],'strategies':[s['strategy'] for s in state['strategies']]})}],'response_format':{'type':'json_object'},'temperature':0}
        try:
            response=requests.post(os.getenv('LLM_BASE_URL','https://api.openai.com/v1').rstrip('/')+'/chat/completions',headers={'Authorization':f'Bearer {key}'},json=payload,timeout=25)
            response.raise_for_status()
            report['llm_draft']=Narrative.model_validate_json(response.json()['choices'][0]['message']['content']).model_dump()
            report['narrative_mode']='LLM draft — analyst review required; structured evidence is authoritative'
        except (requests.RequestException,ValueError,KeyError,IndexError):
            report['narrative_mode']='deterministic fallback — LLM unavailable or invalid'
    return {'report':report}
