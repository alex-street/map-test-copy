
	
  
  async function init() {

    import {mapboxgl} from "https://api.mapbox.com/mapbox-gl-js/v3.10.0/mapbox-gl.js";

    mapboxgl.accessToken = 'pk.eyJ1IjoiYWJyYWRzdHJlZXQiLCJhIjoiY203cWk0eHI1MG85MDJxc2RsdWxhams1ZyJ9.6BgTI4psEojyICyZFsFHlw';
    const map = new mapboxgl.Map({
        // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [-3.195, 55.95],
        zoom: 15.5,
        pitch: 45,
        bearing: -17.6,
        container: 'map',
        antialias: true
    });

    map.on('style.load', () => {

      map.addSource('mapbox-dem', {
            'type': 'raster-dem',
            'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
            'tileSize': 512,
            'maxzoom': 14
        });
        // add the DEM source as a terrain layer with exaggerated height
        map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });

        // Insert the layer beneath any symbol layer.
        const layers = map.getStyle().layers;
        const labelLayerId = layers.find(
            (layer) => layer.type === 'symbol' && layer.layout['text-field']
        ).id;

        // The 'building' layer in the Mapbox Streets
        // vector tileset contains building height data
        // from OpenStreetMap.
        map.addLayer(
            {
                'id': 'add-3d-buildings',
                'source': 'composite',
                'source-layer': 'building',
                'filter': ['==', 'extrude', 'true'],
                'type': 'fill-extrusion',
                'minzoom': 15,
                'paint': {
                    'fill-extrusion-color': '#aaa',

                    // Use an 'interpolate' expression to
                    // add a smooth transition effect to
                    // the buildings as the user zooms in.
                    'fill-extrusion-height': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        15,
                        0,
                        15.05,
                        ['get', 'height']
                    ],
                    'fill-extrusion-base': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        15,
                        0,
                        15.05,
                        ['get', 'min_height']
                    ],
                    'fill-extrusion-opacity': 0.6
                }
            },
            labelLayerId
        );
    });


    const response = await fetch('/get_lat_long');
    const locations = await response.json();
    locations.forEach(item => {

      console.log(`Lat: ${item.lat}, Lon: ${item.lon}`);

      const el = document.createElement('div');
      el.className = 'marker';
      new mapboxgl.Marker(el).setLngLat([item.lon, item.lat])
      .setPopup(
            new mapboxgl.Popup({ offset: 25 }) // add popups
              .setHTML(
                `<h3>${item.text}</h3><p>${item.freq}</p>`
              )
          ).addTo(map);

      
    });
  }
  init();
