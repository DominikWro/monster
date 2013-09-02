function getMemInfoAndBakePie() {
  $.ajax('/api/mem_info/1', { dataType: 'json' }).done(function(response) {
    var memTable = [];
    memTable[0] = ['Type', 'MB'];
    if (response.mem_info[0].hasOwnProperty('cached')) {
      /* Linux. */
      memTable[1] = ['Free', response.mem_info[0]['free']];
      memTable[2] = ['Used', response.mem_info[0]['used']]; 
      memTable[3] = ['Cached', response.mem_info[0]['cached']]; 
    } else {
      /* OSX */
      memTable[1] = ['Free', response.mem_info[0]['free']];
      memTable[2] = ['Active', response.mem_info[0]['active']]; 
      memTable[3] = ['Inactive', response.mem_info[0]['inactive']]; 
      memTable[4] = ['Wired', response.mem_info[0]['wired']]; 
    }
    var pieData = google.visualization.arrayToDataTable(memTable);
    var options = {
      colors: ['#ff2d55', '#5ac8fa', '#4cd964', '#ffcc00'],
      pieSliceText: 'value',
      fontName: 'maven pro'
    };
    var chart = new google.visualization.PieChart(document.getElementById('memory_pie'));
    chart.draw(pieData, options);
    
    if (!pie_refresh) {
      pie_refresh = setInterval(getMemInfoAndBakePie, 3000); 
    }
  }); 
}

function getMemInfoAndPaintLayers() {
  $.ajax('/api/mem_info/30', { dataType: 'json' }).done(function(response) {
    var memTable = [];
    if (response.mem_info[0].hasOwnProperty('cached')) {
      memTable[0] = ['Index', 'Used', 'Cached', 'Free'];
      for (var i = 0; i < response.mem_info.length; i++) {
        memEntry = [
          i,
          response.mem_info[i]['used'],
          response.mem_info[i]['cached'],
          response.mem_info[i]['free']
        ];
        memTable.push(memEntry);
      }
    } else {
      memTable[0] = ['Index', 'Wired', 'Active', 'Inactive', 'Free'];
      for (var i = 0; i < response.mem_info.length; i++) {
        memEntry = [
          i,
          response.mem_info[i]['wired'],
          response.mem_info[i]['active'],
          response.mem_info[i]['inactive'],
          response.mem_info[i]['free']
        ];
        memTable.push(memEntry);
      }
    }
    var areaData = new google.visualization.arrayToDataTable(memTable);
    var options = {
      colors: ['#ff2d55', '#5ac8fa', '#4cd964', '#ffcc00'],
      isStacked: true,
      areaOpacity: 0.8,
      fontName: 'maven pro',
      hAxis: {
        gridlines: {
          color: '#f6f6f6'
        }
      },
      vAxis: {
        gridlines:{color: '#f6f6f6'}}
    };
    var chart = new google.visualization.AreaChart(document.getElementById('memory_area'));
    chart.draw(areaData, options);

    if (!area_refresh) {
      area_refresh = setInterval(getMemInfoAndPaintLayers, 3000);
    }
  }); 
}
