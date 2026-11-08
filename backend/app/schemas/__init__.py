from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class CustomerFeatures(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    CreditScore:int=Field(ge=300,le=900)
    Geography:Literal['France','Germany','Spain']
    Gender:Literal['Female','Male']
    Age:int=Field(ge=18,le=110)
    Tenure:int=Field(ge=0,le=60)
    Balance:float=Field(ge=0,le=1e10)
    NumOfProducts:int=Field(ge=1,le=4)
    HasCrCard:Literal[0,1]
    IsActiveMember:Literal[0,1]
    EstimatedSalary:float=Field(ge=0,le=1e10)

class Narrative(BaseModel):
    model_config=ConfigDict(extra='forbid')
    summary:str=Field(max_length=1200)
    questions_for_analyst:list[str]=Field(max_length=5)
