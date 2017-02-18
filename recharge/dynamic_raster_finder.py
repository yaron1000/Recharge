# ===============================================================================
# Copyright 2016 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
"""
The purpose of this module is to find a raster file for a specified day.

this module provides (2) function -- find_ndvi, find_prism.
run_distributed_ETRM does all the work

dgketchum 24 JUL 2016
"""

import os
from numpy import where, isnan

from recharge.raster_tools import convert_raster_to_array, apply_mask
from recharge.point_extract_utility import get_inputs_at_point

NUMS = (1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177, 193, 209,
        225, 241, 257, 273, 289, 305, 321, 337, 353)
PRISM_YEARS = (2000, 2001, 2003, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013)


def get_kcb(mask_path, in_path, date_object, previous_kcb=None, coords=None):
    """
    Find NDVI image and convert to Kcb.

    :param in_path: NDVI input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :param previous_kcb: Previous day's kcb value.
    :param coords: Call if using to get point data using point_extract_utility.
    :return: numpy array object
    """
    # print date_object
    doy = date_object.timetuple().tm_yday
    year = date_object.year

    if year == 2000:
        band = 1
        raster = '{}_{}.tif'.format(year, doy)
    elif year == 2001:
        for num in NUMS:
            diff = doy - num
            if 0 <= diff <= 15:
                start = num
                if num == 353:
                    nd = num + 12
                else:
                    nd = num + 15

                band = diff + 1
                raster = '{}_{}_{}.tif'.format(year, start, nd)
                break
    else:
        for i, num in enumerate(NUMS):
            diff = doy - num
            if 0 <= diff <= 15:
                band = diff + 1
                raster = '{}_{}.tif'.format(year, i + 1)
                break

    if coords:
        ndvi = get_inputs_at_point(coords, os.path.join(in_path, raster))
        kcb = ndvi * 1.25
        return kcb

    else:
        ndvi = apply_mask(mask_path, convert_raster_to_array(in_path, raster, band=band))

        kcb = ndvi * 1.25

        if previous_kcb is None:
            pass
        else:
            kcb = where(isnan(kcb) is True, previous_kcb, kcb)
            kcb = where(abs(kcb) > 100., previous_kcb, kcb)

        return kcb


def get_prism(mask_path, in_path, date_object, coords=None):
    """
    Find PRISM image.

    :param variable: type of PRISM variable sought
    :type variable: str
    :param in_path: PRISM input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :param coords: Call if using to get point data using point_extract_utility.
    :type coords: str
    :return: numpy array object
    """
    year = date_object.year
    tail = '{}{:02n}{:02n}.tif'.format(year, date_object.month, date_object.day)

    if variable == 'precip':

        root = os.path.join(in_path, 'precip', '800m_std_all')  # this will need to be fixed
        raster = 'PRISMD2_NMHW2mi_{}'.format(tail)

    elif variable == 'min_temp':
        root = os.path.join(in_path, 'Temp', 'Minimum_standard')
        if year in PRISM_YEARS:
            raster = 'cai_tmin_us_us_30s_{}'.format(tail)
        else:
            raster = 'TempMin_NMHW2Buff_{}'.format(tail)

    elif variable == 'max_temp':
        root = os.path.join(in_path, 'Temp', 'Maximum_standard')
        raster = 'TempMax_NMHW2Buff_{}'.format(tail)

    if coords:
        ret = get_inputs_at_point(coords, os.path.join(root, raster))
    else:
        ret = convert_raster_to_array(root, raster)

    return apply_mask(mask_path, ret)


def get_penman(mask_path, in_path, date_object, variable='etrs', coords=None):
    """
    Find PENMAN image.

    :param variable: type of PENMAN variable sought
    :type variable: str
    :param in_path: PENMAN input data path.
    :type in_path: str
    :param date_object: Datetime object of date.
    :param coords: Call if using to get point data using point_extract_utility.
    :type coords: str
    :return: numpy array object
    """

    year = date_object.year
    tail = '{}_{:03n}.tif'.format(year, date_object.timetuple().tm_yday)

    if variable == 'etrs':
        raster = os.path.join('PM{}'.format(year), 'PM_NM_{}'.format(tail))

    elif variable == 'rlin':
        raster = os.path.join('PM{}'.format(year), 'RLIN_NM_{}'.format(tail))

    elif variable == 'rg':
        raster = os.path.join('rad{}'.format(year), 'RTOT_{}'.format(tail))

    if coords:
        ret = get_inputs_at_point(coords, os.path.join(in_path, raster))
    else:
        ret = convert_raster_to_array(in_path, raster)

    return apply_mask(mask_path, ret)

# ============= EOF =============================================
