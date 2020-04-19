import os
import pandas as pd
from frozendict import frozendict
from pm4pymdl.algo.mvp.gen_framework import factory as discovery
from pm4pymdl.visualization.mvp.gen_framework import factory as vis_factory
from pm4pymdl.algo.mvp.utils import clean_frequency, clean_arc_frequency

dir = r"C:\Users\aless\Documents\sap_extraction"


class Shared:
    ekbe = {}
    ekpo = {}
    activities = {}
    events = {}


def read_activities():
    tstct = pd.read_csv(os.path.join(dir, "TSTCT.tsv"), sep="\t")
    tstct = tstct[tstct["SPRSL"] == "E"]
    tstct = tstct[["TCODE", "TTEXT"]]
    stream = tstct.to_dict("r")
    for row in stream:
        Shared.activities[row["TCODE"]] = row["TTEXT"]


def remove_zeros(stru):
    i = 0
    while i < len(stru):
        if not stru[i] == "0":
            return stru[i:]
        i = i + 1
    return stru


def read_ekbe():
    ekbe = pd.read_csv(os.path.join(dir, "ekbe.tsv"), sep="\t")
    ekbe = ekbe[["BELNR", "EBELN"]]
    ekbe = ekbe.dropna(subset=["BELNR"])
    ekbe = ekbe.dropna(subset=["EBELN"])
    stream = ekbe.to_dict("r")
    for row in stream:
        Shared.ekbe[str(row["BELNR"])] = str(row["EBELN"])


def read_ekpo():
    ekpo = pd.read_csv(os.path.join(dir, "ekpo.tsv"), sep="\t")
    ekpo = ekpo[["BANFN", "EBELN"]]
    ekpo = ekpo.dropna(subset=["BANFN"])
    ekpo = ekpo.dropna(subset=["EBELN"])
    stream = ekpo.to_dict("r")
    for row in stream:
        Shared.ekpo[str(row["EBELN"])] = str(int(row["BANFN"]))


def extract_cdhdr():
    cdhdr = pd.read_csv(os.path.join(dir, "cdhdr.tsv"), sep="\t")
    cdhdr = cdhdr[["OBJECTCLAS", "OBJECTID", "USERNAME", "UDATE", "UTIME", "TCODE", "CHANGENR"]]
    cdpos = pd.read_csv(os.path.join(dir, "cdpos.tsv"), sep="\t")
    cdpos = cdpos[["CHANGENR", "VALUE_NEW"]]
    merged = pd.merge(cdhdr, cdpos, left_on="CHANGENR", right_on="CHANGENR", suffixes=["", "_2"])
    merged = merged.dropna(subset=["VALUE_NEW"])
    merged = merged[merged["VALUE_NEW"].isin(merged["OBJECTID"])]
    merged = pd.merge(merged, cdhdr, left_on="VALUE_NEW", right_on="OBJECTID", suffixes=["", "_3"])
    merged = merged.rename(columns={"USERNAME": "event_resource", "TCODE": "event_activity"})
    merged["event_timestamp"] = merged["UDATE"] + " " + merged["UTIME"]
    merged["event_timestamp"] = pd.to_datetime(merged["event_timestamp"], format="%d.%m.%Y %H:%M:%S")
    merged = merged.dropna(subset=["event_activity"])
    merged = merged.dropna(subset=["event_resource"])
    stream = merged.to_dict("r")
    for ev in stream:
        ev["OBJECTID"] = remove_zeros(ev["OBJECTID"])
        ev["OBJECTID_3"] = remove_zeros(ev["OBJECTID_3"])
        key = frozendict({"event_timestamp": ev["event_timestamp"],
                          "event_resource": ev["event_resource"], "event_activity": ev["event_activity"]})
        if key not in Shared.events:
            Shared.events[key] = set()
        Shared.events[key].add(frozendict({ev["OBJECTCLAS"]: ev["OBJECTID"]}))
        Shared.events[key].add(frozendict({ev["OBJECTCLAS_3"]: ev["OBJECTID_3"]}))


def extract_rbkp():
    rbkp = pd.read_csv(os.path.join(dir, "rbkp.tsv"), sep="\t")
    rbkp = rbkp[["BELNR", "CPUDT", "CPUTM", "USNAM", "TCODE"]]
    rbkp = rbkp[rbkp["BELNR"].isin(Shared.ekbe.keys())]
    rbkp = rbkp.rename(columns={"USNAM": "event_resource", "TCODE": "event_activity"})
    rbkp["event_timestamp"] = rbkp["CPUDT"] + " " + rbkp["CPUTM"]
    rbkp["event_timestamp"] = pd.to_datetime(rbkp["event_timestamp"], format="%d.%m.%Y %H:%M:%S")
    rbkp = rbkp.dropna(subset=["event_activity"])
    rbkp = rbkp.dropna(subset=["event_resource"])
    stream = rbkp.to_dict("r")
    for ev in stream:
        key = frozendict({"event_timestamp": ev["event_timestamp"],
                          "event_resource": ev["event_resource"], "event_activity": ev["event_activity"]})
        if key not in Shared.events:
            Shared.events[key] = set()
        Shared.events[key].add(frozendict({"BELNR": str(ev["BELNR"])}))


def extract_bkpf():
    bkpf = pd.read_csv(os.path.join(dir, "bkpf.tsv"), sep="\t")
    bkpf = bkpf[["BELNR", "CPUDT", "CPUTM", "USNAM", "TCODE"]]
    bkpf = bkpf[bkpf["BELNR"].isin(Shared.ekbe.keys())]
    bkpf = bkpf.rename(columns={"USNAM": "event_resource", "TCODE": "event_activity"})
    bkpf["event_timestamp"] = bkpf["CPUDT"] + " " + bkpf["CPUTM"]
    bkpf["event_timestamp"] = pd.to_datetime(bkpf["event_timestamp"], format="%d.%m.%Y %H:%M:%S")
    bkpf = bkpf.dropna(subset=["event_activity"])
    bkpf = bkpf.dropna(subset=["event_resource"])
    stream = bkpf.to_dict("r")
    for ev in stream:
        key = frozendict({"event_timestamp": ev["event_timestamp"],
                          "event_resource": ev["event_resource"], "event_activity": ev["event_activity"]})
        if key not in Shared.events:
            Shared.events[key] = set()
        Shared.events[key].add(frozendict({"BELNR": str(ev["BELNR"])}))


def extract_eban():
    eban = pd.read_csv(os.path.join(dir, "eban.tsv"), sep="\t")
    eban = eban[["BANFN", "ERDAT", "ERNAM"]]
    eban = eban.rename(columns={"ERNAM": "event_resource", "ERDAT": "event_timestamp"})
    eban["event_timestamp"] = pd.to_datetime(eban["event_timestamp"], format="%d.%m.%Y")
    eban["event_activity"] = "ME51N"
    eban = eban.dropna(subset=["event_activity"])
    eban = eban.dropna(subset=["event_resource"])
    stream = eban.to_dict("r")
    for ev in stream:
        key = frozendict({"event_timestamp": ev["event_timestamp"],
                          "event_resource": ev["event_resource"], "event_activity": ev["event_activity"]})
        if key not in Shared.events:
            Shared.events[key] = set()
        Shared.events[key].add(frozendict({"BANF": str(ev["BANFN"])}))


def extract_ekko():
    ekko = pd.read_csv(os.path.join(dir, "ekko.tsv"), sep="\t")
    ekko = ekko[["EBELN", "BEDAT", "ERNAM"]]
    ekko = ekko.rename(columns={"ERNAM": "event_resource", "BEDAT": "event_timestamp"})
    ekko["event_timestamp"] = pd.to_datetime(ekko["event_timestamp"], format="%d.%m.%Y")
    ekko["event_activity"] = "ME21N"
    ekko = ekko.dropna(subset=["event_activity"])
    ekko = ekko.dropna(subset=["event_resource"])
    stream = ekko.to_dict("r")
    for ev in stream:
        key = frozendict({"event_timestamp": ev["event_timestamp"],
                          "event_resource": ev["event_resource"], "event_activity": ev["event_activity"]})
        if key not in Shared.events:
            Shared.events[key] = set()
        ebeln = str(ev["EBELN"])
        Shared.events[key].add(frozendict({"EINKBELEG": ebeln}))

def get_final_dataframe():
    stream = []
    keys = sorted(list(Shared.events.keys()), key=lambda x: x["event_timestamp"])
    id = 0
    for index, key in enumerate(keys):
        id = id + 1
        for obj in Shared.events[key]:
            ev = dict(key)
            ev.update(dict(obj))
            ev["event_id"] = str(id)
            stream.append(ev)
            act = ev["event_activity"]
            ev["event_activity"] = Shared.activities[act] if act in Shared.activities else act
    dataframe = pd.DataFrame(stream)
    dataframe.type = "exploded"
    return dataframe


def insert_ekpo_information():
    events = sorted(list(Shared.events.keys()), key=lambda x: x["event_timestamp"])
    ebeln_map = {}
    for index, eve in enumerate(events):
        eve_map = dict()
        for val in Shared.events[eve]:
            for k in val:
                eve_map[k] = val[k]
        if "EINKBELEG" in eve_map:
            val = eve_map["EINKBELEG"]
            if val in Shared.ekpo:
                ebeln_map[val] = eve
    for n in ebeln_map:
        eve = ebeln_map[n]
        corr = Shared.ekpo[n]
        Shared.events[eve].add(frozendict({"BANF": corr}))


def insert_ekbe_information():
    events = sorted(list(Shared.events.keys()), key=lambda x: x["event_timestamp"])
    belnr_map = {}
    for index, eve in enumerate(events):
        eve_map = dict()
        for val in Shared.events[eve]:
            for k in val:
                eve_map[k] = val[k]
        if "BELNR" in eve_map:
            val = eve_map["BELNR"]
            if val in Shared.ekbe:
                belnr_map[val] = eve
    for n in belnr_map:
        eve = belnr_map[n]
        corr = Shared.ekbe[n]
        Shared.events[eve].add(frozendict({"EINKBELEG": corr}))


if __name__ == "__main__":
    read_ekpo()
    #print(Shared.ekpo)
    read_ekbe()
    read_activities()
    extract_cdhdr()
    extract_rbkp()
    extract_bkpf()
    extract_eban()
    extract_ekko()
    insert_ekpo_information()
    insert_ekbe_information()
    if True:
        dataframe = get_final_dataframe()
        dataframe = clean_frequency.apply(dataframe, 50)
    if True:
        model = discovery.apply(dataframe, model_type_variant="model2", node_freq_variant="type21",
                                edge_freq_variant="type211")
        gviz = vis_factory.apply(model, parameters={"format": "svg", "min_edge_freq": 50})
        vis_factory.view(gviz)
