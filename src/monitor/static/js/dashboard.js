// Update how we handle sensor data, particularly for ink levels which are now threshold-based
function updateSensorData(data) {
  // Update paper level display
  const paperPercentage = data.paper_percentage;
  const paperCount = data.paper_level;
  const paperCapacity = data.paper_capacity;
  
  $('#paperValue').text(paperPercentage + '%');
  $('#paperCount').text(paperCount);
  $('#paperCapacity').text(paperCapacity);
  
  // Update paper gauge
  paperGauge.set(paperPercentage / 100);
  
  // Change color based on paper level
  let paperColor = '#4CAF50'; // Green
  if (paperPercentage < 20) {
    paperColor = '#F44336'; // Red for low paper
  } else if (paperPercentage < 40) {
    paperColor = '#FF9800'; // Orange for medium-low paper
  }
  paperGauge.options.strokeColor = paperColor;
  
  // Update ink levels - now binary threshold-based displays
  for (const [color, level] of Object.entries(data.ink_levels)) {
    const $inkElement = $(`#${color}Ink`);
    const $statusElement = $(`#${color}InkStatus`);
    
    // Set fill height based on percentage
    $inkElement.find('.ink-fill').css('height', `${level}%`);
    
    // Set color and status text based on level
    let inkColor, statusText;
    if (level < 20) {
      inkColor = '#F44336'; // Red
      statusText = 'LOW';
      $statusElement.addClass('status-warning');
    } else {
      inkColor = color === 'black' ? '#000' : 
                 color === 'cyan' ? '#00BCD4' : 
                 color === 'magenta' ? '#E91E63' : 
                 color === 'yellow' ? '#FFC107' : '#666';
      statusText = 'OK';
      $statusElement.removeClass('status-warning');
    }
    
    $inkElement.find('.ink-fill').css('background-color', inkColor);
    $statusElement.text(statusText);
  }
  
  // Update Arduino connection status
  const isConnected = data.arduino_connected === true;
  $('#arduinoStatus').text(isConnected ? 'Connected' : 'Disconnected')
    .removeClass(isConnected ? 'status-error' : 'status-success')
    .addClass(isConnected ? 'status-success' : 'status-error');
} 