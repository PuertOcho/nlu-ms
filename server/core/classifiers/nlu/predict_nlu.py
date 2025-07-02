# -*- coding: utf-8 -*-
import os
import asyncio
from collections import OrderedDict
from utils import nlp_config
from warnings import simplefilter
from rasa.core.agent import Agent

from rasa.shared.nlu.training_data.loading import load_data
from rasa.shared.utils.io import json_to_string
from utils import log_util

scriptDir = os.path.dirname(__file__)
dataFile = ""

simplefilter(action='ignore')

# Cache global para modelos y bucle de eventos
_model_cache = {}
_event_loop = None

def get_or_create_event_loop():
    """Obtiene o crea un bucle de eventos reutilizable"""
    global _event_loop
    if _event_loop is None or _event_loop.is_closed():
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_event_loop)
    return _event_loop

def get_cached_agent(domain, locale):
    """Obtiene un agente cacheado o lo carga si no existe"""
    model_key = f"{domain}_{locale}"
    
    if model_key not in _model_cache:
        modelPath = os.path.join(scriptDir, '..', '..', 'models', 'nlu')
        log_util.log_infomsg(f"[PREDICT_NLU] Cargando modelo para {model_key}...")
        _model_cache[model_key] = Agent.load(model_path=modelPath)
        log_util.log_infomsg(f"[PREDICT_NLU] Modelo {model_key} cacheado exitosamente")
    
    return _model_cache[model_key]

def predict(domain, locale, userUtterance):
    global dataFile
    dataFile = os.path.join(scriptDir, '..', '..', '..', 'training_data', 'intents', domain + '_' + locale + '.yml')
    
    # Usar agente cacheado
    agent = get_cached_agent(domain, locale)
    
    # Usar bucle de eventos reutilizable
    loop = get_or_create_event_loop()
    data = loop.run_until_complete(agent.parse_message(userUtterance))

    intent_, score_, utterance_ = [], [], []
    intent_.append(data['intent_ranking'][0]['name'])
    intent_.append(data['intent_ranking'][1]['name'])
    intent_.append(data['intent_ranking'][2]['name'])
    score_.append("{:.2f}".format(data['intent_ranking'][0]['confidence']))
    score_.append("{:.2f}".format(data['intent_ranking'][1]['confidence']))
    score_.append("{:.2f}".format(data['intent_ranking'][2]['confidence']))
    utterance_.append(getUtterance(intent_[0]))
    utterance_.append(getUtterance(intent_[1]))
    utterance_.append(getUtterance(intent_[2]))
    entities_ = data['entities']
    text_ = data['text']
    intent_ranking_ = [{"name": p, "confidence": q, "utterance": r} for p, q, r in zip(intent_, score_, utterance_)]
    intent_top_ = {"name": intent_[0], "confidence": score_[0]}
    # build JSON response
    response = {'intent': intent_top_, 'entities': entities_, 'intent_ranking': intent_ranking_, 'text': text_}
    log_util.log_infomsg(f"[PREDICT_NLU] prediction: {response}")
    return response


def getUtterance(intent_):
    train_data = load_data(dataFile)
    training_examples = OrderedDict()
    INTENT = 'intent'
    for example in [e.as_dict_nlu() for e in train_data.training_examples]:
        intent = example[INTENT]
        training_examples.setdefault(intent, [])
        training_examples[intent].append(example)
    return training_examples[intent_][0]['text']
