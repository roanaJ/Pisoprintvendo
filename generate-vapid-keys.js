const webpush = require('web-push');

// Generate VAPID keys
const vapidKeys = webpush.generateVAPIDKeys();

console.log('Public Key:', vapidKeys.publicKey);
console.log('Private Key:', vapidKeys.privateKey);

console.log('\nAdd these to your server.js file:');
console.log(`const publicVapidKey = '${vapidKeys.publicKey}';`);
console.log(`const privateVapidKey = '${vapidKeys.privateKey}';`); 