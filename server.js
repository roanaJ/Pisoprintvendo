// Assuming you're using Express.js
const express = require('express');
const webpush = require('web-push');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Replace these placeholder values with your generated keys
const publicVapidKey = 'YOUR_GENERATED_PUBLIC_KEY';
const privateVapidKey = 'YOUR_GENERATED_PRIVATE_KEY';

webpush.setVapidDetails(
  'mailto:your-actual-email@example.com', // Use your actual email
  publicVapidKey,
  privateVapidKey
);

// Store subscriptions (in a real app, use a database)
const subscriptions = [];

// Subscribe endpoint
app.post('/api/subscribe', (req, res) => {
  const subscription = req.body;
  subscriptions.push(subscription);
  res.status(201).json({});
});

// Function to send error notifications
function sendErrorNotification(error) {
  const payload = JSON.stringify({
    title: 'PisoPrint Error',
    body: `Error detected: ${error}`,
    url: '/dashboard'
  });

  subscriptions.forEach(subscription => {
    webpush.sendNotification(subscription, payload)
      .catch(err => {
        console.error('Error sending notification:', err);
        // Remove invalid subscriptions
        if (err.statusCode === 410) {
          const index = subscriptions.indexOf(subscription);
          if (index !== -1) subscriptions.splice(index, 1);
        }
      });
  });
}

// Function to send low resource warnings
function sendLowResourceWarning(resource, level) {
  const payload = JSON.stringify({
    title: 'PisoPrint Resource Warning',
    body: `Low ${resource} detected: ${level}%`,
    url: '/resources'
  });

  subscriptions.forEach(subscription => {
    webpush.sendNotification(subscription, payload)
      .catch(err => {
        console.error('Error sending notification:', err);
        if (err.statusCode === 410) {
          const index = subscriptions.indexOf(subscription);
          if (index !== -1) subscriptions.splice(index, 1);
        }
      });
  });
}

// Example: Monitor system resources
function monitorResources() {
  // This is where you'd integrate with your actual monitoring system
  // For example, checking printer filament levels, memory usage, etc.
  
  // Example implementation:
  if (filamentLevel < 10) {
    sendLowResourceWarning('filament', filamentLevel);
  }
  
  if (diskSpace < 15) {
    sendLowResourceWarning('disk space', diskSpace);
  }
}

// Error notification endpoint
app.post('/api/notify/error', (req, res) => {
  const { source, message, timestamp } = req.body;
  
  // Log error to system log
  console.error(`[${timestamp}] Error from ${source}: ${message}`);
  
  // Send push notification to all subscribers
  const payload = JSON.stringify({
    title: 'PisoPrint Error',
    body: message,
    url: '/dashboard',
    timestamp
  });
  
  subscriptions.forEach(subscription => {
    webpush.sendNotification(subscription, payload)
      .catch(handlePushError);
  });
  
  res.status(200).json({ success: true });
});

// Resource warning notification endpoint
app.post('/api/notify/resource', (req, res) => {
  const { resource, level, message, timestamp } = req.body;
  
  // Log warning to system log
  console.warn(`[${timestamp}] Resource warning for ${resource}: ${level}% - ${message}`);
  
  // Send push notification to all subscribers
  const payload = JSON.stringify({
    title: 'PisoPrint Resource Warning',
    body: message,
    url: '/resources',
    timestamp
  });
  
  subscriptions.forEach(subscription => {
    webpush.sendNotification(subscription, payload)
      .catch(handlePushError);
  });
  
  res.status(200).json({ success: true });
});

// Handle push errors and clean up invalid subscriptions
function handlePushError(err) {
  console.error('Error sending notification:', err);
  
  // Remove invalid subscriptions
  if (err.statusCode === 410) {
    const index = subscriptions.indexOf(subscription);
    if (index !== -1) subscriptions.splice(index, 1);
  }
}

// Mock API for system status (replace with actual implementation)
app.get('/api/system/status', (req, res) => {
  // In a real implementation, you would get this data from your actual printer system
  const mockStatus = {
    filament: {
      level: Math.floor(Math.random() * 100), // Random level for demo
      type: 'PLA',
      color: 'Blue'
    },
    paper: {
      level: Math.floor(Math.random() * 100),
      size: 'A4'
    },
    ink: {
      level: Math.floor(Math.random() * 100),
      type: 'Standard'
    },
    system: {
      memoryUsage: Math.floor(Math.random() * 100),
      cpuUsage: Math.floor(Math.random() * 100),
      diskSpace: Math.floor(Math.random() * 100)
    },
    hardware: {
      temperature: 35 + Math.floor(Math.random() * 30),
      status: 'ready',
      errors: []
    },
    jobs: {
      active: Math.floor(Math.random() * 3),
      queued: Math.floor(Math.random() * 5),
      completed: 125
    }
  };
  
  // Randomly generate errors for testing
  if (Math.random() < 0.1) { // 10% chance of error
    mockStatus.hardware.errors.push({
      code: 'E' + Math.floor(Math.random() * 100),
      message: 'Random hardware error for testing'
    });
  }
  
  res.json(mockStatus);
});

// Start server
app.listen(3000, () => {
  console.log('Server started on port 3000');
}); 