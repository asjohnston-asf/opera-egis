import os
import uuid
from pathlib import Path

import boto3
import requests
from osgeo import gdal, osr


gdal.UseExceptions()
os.environ['GDAL_DISABLE_READDIR_ON_OPEN'] = 'EMPTY_DIR'
s3 = boto3.client('s3')


def get_auth():
    response = requests.get(
        'https://urs.earthdata.nasa.gov/oauth/authorize?client_id=BO_n7nTIlMljdvU6kRRB3g&response_type=code&redirect_uri=https://cumulus.asf.alaska.edu/login&state=%2Fs3credentials&app_type=401',
        auth=(os.environ['USERNAME'], os.environ['PASSWORD']),
    )
    response.raise_for_status()
    credentials = response.json()
    os.environ['AWS_ACCESS_KEY_ID'] = credentials['accessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['secretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = credentials['sessionToken']


def get_pixel_type(data_type: str) -> int:
    if data_type == 'Byte':
        return 3
    if data_type == 'Float32':
        return 9
    raise ValueError(f'Unsupported data type: {data_type}')


def get_projection(srs_wkt: str) -> str:
    srs = osr.SpatialReference()
    srs.ImportFromWkt(srs_wkt)
    return srs.GetAttrValue('AUTHORITY', 1)


def get_raster_metadata(raster_path: str) -> dict:
    name = Path(raster_path).stem
    download_url = f'https://datapool.asf.alaska.edu/RTC/OPERA-S1/{name}.tif'
    acquisition_date = \
        name[36:38] + '/' + name[38:40] + '/' + name[32:36] + ' ' + name[41:43] + ':' + name[43:45] + ':' + name[45:47]
    info = gdal.Info(raster_path, format='json')
    return {
        'Raster': info['description'],
        'Name': name,
        'xMin': info['cornerCoordinates']['lowerLeft'][0],
        'yMin': info['cornerCoordinates']['lowerLeft'][1],
        'xMax': info['cornerCoordinates']['upperRight'][0],
        'yMax': info['cornerCoordinates']['upperRight'][1],
        'nRows': info['size'][1],
        'nCols': info['size'][0],
        'nBands': len(info['bands']),
        'PixelType': get_pixel_type(info['bands'][0]['type']),
        'SRS': get_projection(info['coordinateSystem']['wkt']),
        'DownloadURL': download_url,
        'URLDisplay': name,
        'Polarization': name.split('_')[9],
        'StartDate': acquisition_date,
        'EndDate': acquisition_date,
    }


def process_granules(granules):
    get_auth()
    data = [get_raster_metadata(granule) for granule in granules]
    content = '\n'.join([','.join([str(value) for value in item.values()]) for item in data])
    del os.environ['AWS_ACCESS_KEY_ID']
    del os.environ['AWS_SECRET_ACCESS_KEY']
    del os.environ['AWS_SESSION_TOKEN']
    s3.put_object(Bucket=os.environ['BUCKET'], Key=f'opera-egis/{str(uuid.uuid4())}', Body=content)


def lambda_handler(event, context):
    granules = [record['body'] for record in event['Records']]
    process_granules(granules)
