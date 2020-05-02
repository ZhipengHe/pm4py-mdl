import pandas as pd
from pm4pymdl.algo.mvp.gen_framework2 import general
from pm4pymdl.algo.mvp.utils import clean_frequency, clean_arc_frequency
from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.log import EventStream
from pm4py.algo.discovery.inductive import factory as inductive_miner

def apply(df0, classifier_function=None, parameters=None):
    if parameters is None:
        parameters = {}

    if classifier_function is None:
        classifier_function = lambda x: x["event_activity"]

    min_acti_freq = parameters["min_acti_freq"] if "min_acti_freq" in parameters else 0
    min_edge_freq = parameters["min_edge_freq"] if "min_edge_freq" in parameters else 0

    df = df0.copy()
    df = general.preprocess(df, parameters=parameters)

    df = clean_frequency.apply(df, min_acti_freq=min_acti_freq)
    df = clean_arc_frequency.apply(df, min_freq=min_edge_freq)

    models = {}
    activities = df.groupby("event_id").first().reset_index()["event_activity"].value_counts()

    obj_types = [x for x in df.columns if not x.startswith("event_")]
    for ot in obj_types:
        new_df = df[["event_id", "event_activity", "event_timestamp", ot]].dropna(subset=[ot])
        new_df = new_df.rename(
            columns={ot: "case:concept:name", "event_activity": "concept:name", "event_timestamp": "time:timestamp"})
        log = new_df.to_dict("r")
        log = EventStream(log)
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG)

        models[ot] = inductive_miner.apply_tree(log, parameters=parameters)

    return {"type": "ptree", "models": models, "activities": activities}
