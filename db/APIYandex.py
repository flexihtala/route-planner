import requests


class YandexApiGeocoderParser:
    def __init__(self, apikey='4a4752ab-1d5e-4025-a203-7cc8b10e5f24'):
        self.apikey = apikey
        self.session = requests.Session()

    def get_cords(self, address: str) -> tuple[float, float] | None:
        """По строке вида 'City, street, house_number' выдает координаты этого места
        :param address: адресс вида 'City, street, house_number'
        :return: кортеж из координат, если удалось найти. Иначе None
        """

        parameters = {
            'apikey': self.apikey,
            'geocode': address,
            'format': 'json'
        }

        url = 'https://geocode-maps.yandex.ru/1.x/?' + '&'.join(
            [f'{key}={value}' for key, value in parameters.items()])

        response = self.session.get(url)
        if response.status_code != 200:
            return None

        data = response.json()

        if data['response']['GeoObjectCollection']['metaDataProperty'][
            'GeocoderResponseMetaData']['found'] == '0':
            return None

        for item in data['response']['GeoObjectCollection']['featureMember']:
            answer = self._get_cords_in_ekb(item)
            if answer:
                return answer
        return None

    def _get_cords_in_ekb(self, geo_object) -> tuple[float, float] | None:
        cord = geo_object['GeoObject']['Point']['pos'].split()
        components = geo_object['GeoObject']['metaDataProperty']['GeocoderMetaData'][
            'Address']['Components']
        for component in components:
            if component['kind'] == 'country':
                if component['name'] != 'Россия': return None
            elif component['kind'] == 'locality':
                if component['name'] != 'Екатеринбург': return None

        return float(cord[0]), float(cord[1])
