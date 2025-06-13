// Add handlers for Arduino sensor calibration
$(document).ready(function() {
  // Tare scale button
  $('#tareScaleBtn').click(function() {
    sendArduinoCommand('tare');
  });
  
  // Calibrate empty tray
  $('#calibrateEmptyBtn').click(function() {
    if (confirm('Make sure the paper tray is completely empty before calibrating.')) {
      sendArduinoCommand('calibrate_empty');
    }
  });
  
  // Calibrate full tray
  $('#calibrateFullBtn').click(function() {
    if (confirm('Make sure the paper tray has exactly 50 sheets before calibrating.')) {
      sendArduinoCommand('calibrate_full');
    }
  });
  
  // Test sensors
  $('#testSensorsBtn').click(function() {
    sendArduinoCommand('test_sensors', {}, function(response) {
      if (response.ink_readings) {
        for (const [color, reading] of Object.entries(response.ink_readings)) {
          $(`#${color}SensorValue`).text(reading);
        }
      }
      if (response.weight_reading) {
        $('#currentWeight').text(response.weight_reading.split(':')[1]);
      }
    });
  });
  
  // Connect to Arduino
  $('#connectArduinoBtn').click(function() {
    const port = $('#arduinoPort').val();
    sendArduinoCommand('connect', { port: port });
  });
  
  // Helper function to send Arduino commands
  function sendArduinoCommand(command, params = {}, callback) {
    $.ajax({
      url: '/api/arduino',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        command: command,
        params: params
      }),
      success: function(data) {
        if (data.status === 'ok') {
          showMessage(`Command ${command} executed successfully`, 'success');
          if (callback) callback(data.response);
        } else {
          showMessage(`Error: ${data.error || 'Unknown error'}`, 'error');
        }
      },
      error: function(xhr, status, error) {
        showMessage(`Request failed: ${error}`, 'error');
      }
    });
  }
  
  // Helper function to show messages
  function showMessage(message, type) {
    const messageDiv = $('<div>')
      .addClass(`alert alert-${type}`)
      .text(message);
    
    $('.message-container').append(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      messageDiv.fadeOut(500, function() {
        $(this).remove();
      });
    }, 5000);
  }
}); 