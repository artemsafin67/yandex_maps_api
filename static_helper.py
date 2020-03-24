def define_coords(toponym_to_find):

    import requests

    geocoder_api_server = 'http://geocode-maps.yandex.ru/1.x/'
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)
    json_response = response.json()

    toponym = json_response['response']['GeoObjectCollection'][
        'featureMember'][0]['GeoObject']
    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()

    toponym_lower_corner, toponym_upper_corner = toponym['boundedBy']['Envelope']['lowerCorner'], \
                                                 toponym['boundedBy']['Envelope']['upperCorner']
    toponym_lower_corner = list(map(float, toponym_lower_corner.split()))
    toponym_upper_corner = list(map(float, toponym_upper_corner.split()))

    toponym_width = abs(toponym_lower_corner[1] - toponym_upper_corner[1])
    toponym_height = abs(toponym_lower_corner[0] - toponym_upper_corner[0])

    toponym_address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']

    try:
        toponym_post_index = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
    except KeyError:
        toponym_post_index = False

    delta = (toponym_width ** 2 + toponym_height ** 2) ** 0.5 / 64
    center = (toponym_longitude, toponym_lattitude)

    return str(delta), center, toponym_address, toponym_post_index

