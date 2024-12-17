document.getElementById('searchButton').addEventListener('click', () => {
  const address = document.getElementById('address').value;
  const radius = document.getElementById('radius').value;
  const placeTypes = Array.from(document.getElementById('placeTypes').selectedOptions)
                          .map(option => option.value);

  if (!address || !radius || placeTypes.length === 0) {
    alert('Пожалуйста, заполните все поля!');
    return;
  }

  const requestData = {
    address: address,
    radius: parseFloat(radius),
    place_type: placeTypes
  };

  fetch('http://127.0.0.1:8080/api/places/search/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Ответ от сервера не OK');
    }
    return response.json();
  })
  .then(data => {
    const mapContainer = document.getElementById('map');
    mapContainer.innerHTML = ''; // Очистка предыдущей карты

    ymaps.ready(() => {
      const myMap = new ymaps.Map("map", {
        center: [55.751244, 37.618423], // Москва по умолчанию
        zoom: 12
      });

      myMap.geoObjects.removeAll(); // Удаление предыдущих меток

      const points = [];

      if (data && Array.isArray(data.results) && data.results.length > 0) {
        data.results.forEach(place => {
          const coords = place.coordinates.split(',').map(coord => parseFloat(coord.trim()));
          points.push(coords);

          const placemark = new ymaps.Placemark(coords, {
            balloonContent: `<strong>${place.name}</strong><br>${place.address}`
          }, {
            preset: 'islands#redIcon'
          });

          myMap.geoObjects.add(placemark);
        });

        if (points.length > 1) {
          const multiRoute = new ymaps.multiRouter.MultiRoute({
                referencePoints: points,
                params: {
                        routingMode: "pedestrian"
                }
          }, {
                boundsAutoApply: true
          });

          myMap.geoObjects.add(multiRoute);
        } else {
          alert('Недостаточно точек для построения маршрута.');
        }

        const bounds = myMap.geoObjects.getBounds();
        if (bounds) {
          myMap.setBounds(bounds, { checkZoomRange: true, zoomMargin: 20 });
        }
      } else {
        alert('Нет результатов для отображения.');
      }
    });
  })
  .catch(error => {
    console.error('Ошибка при отправке данных:', error);
    alert('Произошла ошибка. Пожалуйста, попробуйте снова.');
  });
});