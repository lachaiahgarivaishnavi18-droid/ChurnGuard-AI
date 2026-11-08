import operator, time, json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from . import customer_analysis_agent, churn_prediction_agent, churn_explanation_agent, segmentation_agent, retention_strategy_agent, reporting_agent

class State(TypedDict, total=False):
    customer:dict
    analysis:dict
    prediction:dict
    explanation:dict
    segment:dict
    strategies:list
    report:dict
    logs:Annotated[list,operator.add]

def tracked(name,function):
    def node(state):
        start=time.perf_counter(); result=function(state)
        expected={'customer_analysis':'analysis','prediction':'prediction','explanation':'explanation','segmentation':'segment','retention':'strategies','reporting':'report'}[name]
        if not isinstance(result,dict) or expected not in result: raise ValueError('Invalid agent output')
        json.dumps(result,allow_nan=False)
        return {**result,'logs':[{'agent':name,'status':'completed','duration_ms':round((time.perf_counter()-start)*1000,2)}]}
    return node

def build_graph():
    graph=StateGraph(State)
    for name,module in [('customer_analysis',customer_analysis_agent),('prediction',churn_prediction_agent),('explanation',churn_explanation_agent),('segmentation',segmentation_agent),('retention',retention_strategy_agent),('reporting',reporting_agent)]:
        graph.add_node(name,tracked(name,module.run),retry_policy=RetryPolicy(max_attempts=2,retry_on=(TimeoutError,ConnectionError)))
    graph.add_edge(START,'customer_analysis'); graph.add_edge(START,'prediction'); graph.add_edge(START,'segmentation')
    graph.add_edge('prediction','explanation')
    graph.add_edge(['customer_analysis','explanation','segmentation'],'retention')
    graph.add_conditional_edges('retention',lambda s:'reporting' if s.get('strategies') else END)
    graph.add_edge('reporting',END)
    return graph.compile()

def analyze(customer):
    result=build_graph().invoke({'customer':customer,'logs':[]})
    if 'report' not in result: raise ValueError('Workflow incomplete')
    return {**result['report'],'agent_logs':result['logs']}
