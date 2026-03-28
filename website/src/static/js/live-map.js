let planeIconSVG = `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-airplane-fill" viewBox="0 0 16 16">
  <path stroke="black" stroke-width="0.5" d="M6.428 1.151C6.708.591 7.213 0 8 0s1.292.592 1.572 1.151C9.861 1.73 10 2.431 10 3v3.691l5.17 2.585a1.5 1.5 0 0 1 .83 1.342V12a.5.5 0 0 1-.582.493l-5.507-.918-.375 2.253 1.318 1.318A.5.5 0 0 1 10.5 16h-5a.5.5 0 0 1-.354-.854l1.319-1.318-.376-2.253-5.507.918A.5.5 0 0 1 0 12v-1.382a1.5 1.5 0 0 1 .83-1.342L6 6.691V3c0-.568.14-1.271.428-1.849"/>
</svg>`

    // Set map view
    let map = L.map('map').setView([4.80568, 100.990448], 9);

    // Use OpenStreetMap for map visualization
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    let plane_marker = []

    // Get data from server for initialization
    let socket = io();
    
    socket.on('latest_data', function(plane_data) {
      plane_marker_amount = plane_marker.length;
    
      // Remove existing marker
      if (plane_marker_amount> 0) {
        for (let index = 0; index < plane_marker_amount; ++index){
          const removed = plane_marker.pop()
        
          if (removed != undefined) {
            map.removeLayer(removed)
          }
        }
      }    

      for (let index = 0; index < plane_data.length; ++index) {
        const element = plane_data[index];
        
        console.log(element);

        let planeIcon = L.divIcon({
          html: planeIconSVG,
          iconSize: [40, 40],
          className: "leaflet-plane-div"
        });
        let asc_or_desc = "";
        if (parseFloat(element[11]) > 0){
          asc_or_desc = `<span style="color: rgb(20, 167, 59)">Ascending (${element[11]} m/s)</span>`
        }
        else if (parseFloat(element[11]) < 0) {
          asc_or_desc = `<span style="color: rgb(245, 57, 44)">Descending (${element[11]} m/s)</span>`
        }
        else {
          asc_or_desc = `<span style="color: rgb(130, 130, 130)">Flat (${element[11]} m/s)</span>`

        }
        let m = L.marker([element[6], element[5]], {icon: planeIcon, rotationAngle: parseFloat(element[10])}).addTo(map);
        m.bindTooltip(`
          <h2>${element[1]}</h2>
          <hr>
          <b>ICAO24:</b> ${element[0]}<br>
          <b>Origin:</b> ${element[2]}<br>
          <b>Longitude:</b> ${element[5]} <br>
          <b>Lattitude:</b> ${element[6]} <br>
          <b>Altitude:</b> ${element[7]} m<br>
          <b>${asc_or_desc}</b><br> 
          <b>Speed:</b> ${element[9]} m/s<br>
          <b>On ground:</b> ${element[8]} <br>
        `);
        plane_marker.push(m);
      }
    });

    //velocity=data[9]