import xarray
from dateutil.parser import parse
from datetime import datetime, timedelta
import typing
import numpy as np

from .base import IRI

__all__ = ["datetimerange", "timeprofile", "geoprofile"]


def datetimerange(start: datetime, end: datetime, step: timedelta) -> typing.List[datetime]:
    """like range() for datetime"""
    if isinstance(start, str):
        start = parse(start)

    if isinstance(end, str):
        end = parse(end)

    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert isinstance(step, timedelta)

    return [start + i * step for i in range((end - start) // step)]


def timeprofile(tlim: tuple, dt: timedelta, altkmrange: list, glat: float, glon: float) -> xarray.Dataset:
    """compute IRI altitude profile over time range for fixed lat/lon
    """

    times = datetimerange(tlim[0], tlim[1], dt)

    iono: xarray.Dataset = None

    f107 = []
    ap = []
    for time in times:
        iri = IRI(time, altkmrange, glat, glon)
        if iono is None:
            iono = iri
        else:
            iono = xarray.concat((iono, iri), dim="time")

        f107.append(iri.f107)
        ap.append(iri.ap)

    iono.attrs = iri.attrs
    iono.attrs["f107"] = f107
    iono.attrs["ap"] = ap

    return iono


def geoprofile(latrange: typing.Sequence[float], glon: float, altkm: float, time: datetime) -> xarray.Dataset:
    """compute IRI altitude profiles at time, over lat or lon range
    """

    glat = np.arange(*latrange)

    iono: xarray.Dataset = None

    f107 = []
    ap = []
    for l in glat:
        iri = IRI(time, altkmrange=[altkm] * 3, glat=l, glon=glon)
        if iono is None:
            iono = iri
        else:
            iono = xarray.concat((iono, iri), dim="glat")

        f107.append(iri.f107)
        ap.append(iri.ap)

    iono.attrs = iri.attrs
    iono.attrs["f107"] = f107
    iono.attrs["ap"] = ap

    return iono
