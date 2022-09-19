from typing import Any

from app.schemas.cadaster import FoglioParticelleModel, ParticellaBaseModel
from app.schemas.toponimy import CivicoBaseModel, IndirizzoCiviciModel


def _load_cadaster(ok_message: str):
    """Load the result for cadaster."""

    res = None
    if "it.romacapitale.nic.dati.FoglioDTO/2152584666" in ok_message:
        strlist = (
            ok_message.split(
                '["java.util.ArrayList/4159755760",\
"it.romacapitale.nic.dati.FoglioDTO/2152584666",',
            )[1]
            .split("],0,7]")[0]
            .replace('"', "")
        )
        res_list = tuple(strlist.split(","))
        code = res_list[0]
        sheets = list(res_list)
        sheets.remove(code)
        res = dict(sheets=sheets, code=code)
    elif "it.romacapitale.nic.dati.ParticelleDTO/839545403" in ok_message:
        strlist = (
            ok_message.split(
                '["java.util.ArrayList/4159755760",\
"it.romacapitale.nic.dati.ParticelleDTO/839545403",',
            )[1]
            .split("],0,7]")[0]
            .replace('"', "")
        )
        res_list = tuple(strlist.split(","))
        code = res_list[0]
        parcels = list(res_list)
        parcels.remove(code)
        res = dict(parcels=parcels, code=code)
    return res


def _load_toponimy(ok_message: str):
    """Load the result for toponimy."""

    res = None
    if "it.romacapitale.nic.dati.GeocodingStreetDTO/2784276422" in ok_message:
        strlist = (
            ok_message.split(
                '["java.util.ArrayList/4159755760",\
"it.romacapitale.nic.dati.GeocodingStreetDTO/2784276422",',
            )[1]
            .split("],0,7]")[0]
            .replace('"', "")
        )
        res_list = tuple(strlist.split(","))
        code = res_list[0]
        toponyms = list(res_list)
        toponyms.remove(code)
        res = dict(toponyms=toponyms, code=code)
    # handle //OK[0,1,["java.util.ArrayList/4159755760"],0,7]
    elif "java.util.ArrayList/4159755760" in ok_message:
        strlist = ok_message.split(',["java.util.ArrayList/4159755760"]')[
            0
        ].split("//OK[")[1]
        res_list = tuple(strlist.split(","))
        code = res_list[0]
        check = bool(int(code))
        if not check:
            res = None
    elif "java.lang.Boolean/476441737" in ok_message:
        strlist = ok_message.split(',["java.lang.Boolean/476441737"]')[
            0
        ].split("//OK[")[1]
        res_list = tuple(strlist.split(","))
        code = res_list[0]
        check = bool(int(code))
        res = dict(check=str(check), code=code)
    return res


def build_sheets(result: str):
    res_dict = _load_cadaster(result)
    if res_dict:
        if res_dict.get("sheets"):
            resp = [
                FoglioParticelleModel(foglio=item)
                for item in res_dict["sheets"]
            ]
            return resp
        elif res_dict.get("parcels"):
            parcels = FoglioParticelleModel(
                foglio=res_dict["code"],
                particelle=[
                    ParticellaBaseModel(particella=item)
                    for item in res_dict["parcels"]
                ],
            )
            return parcels
        else:
            return None
    else:
        return None


def build_toponyms(
    result: str,
    query: Any,
):
    res_dict = _load_toponimy(result)
    if res_dict:
        if res_dict.get("toponyms"):
            resp = [
                IndirizzoCiviciModel(indirizzo=item)
                for item in res_dict["toponyms"]
            ]
        elif str2bool(res_dict.get("check")):
            resp = [
                IndirizzoCiviciModel(
                    indirizzo=query.indirizzo.upper(),
                    civici=[CivicoBaseModel(civico=query.civico)],
                ),
            ]
        else:
            resp = [
                IndirizzoCiviciModel(
                    indirizzo=query.indirizzo.upper(),
                    civici=[CivicoBaseModel(civico="-1")],
                ),
            ]
        return resp
    else:
        return None


def str2bool(flag: str) -> bool:
    if flag == "True":
        return True
    elif flag == "False":
        return False
    else:
        raise ValueError("Flag value not in True|False")
