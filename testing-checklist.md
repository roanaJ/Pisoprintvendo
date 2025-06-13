# PisoPrint PWA Testing Checklist

## Installation Tests
- [ ] App installs properly on Android devices
- [ ] App installs properly on iOS devices
- [ ] "Add to Home Screen" prompt appears
- [ ] App icon appears on home screen
- [ ] Splash screen displays correctly

## Offline Functionality
- [ ] App loads in offline mode
- [ ] Cached assets are available offline
- [ ] Appropriate offline message shows for uncached content
- [ ] App reconnects gracefully when back online

## Responsive Design
- [ ] UI renders correctly on mobile phones (320px-480px)
- [ ] UI renders correctly on tablets (768px-1024px)
- [ ] UI renders correctly on desktops (1024px+)
- [ ] Touch targets are large enough (min 48px)
- [ ] Text is readable without zooming

## Notifications
- [ ] Permission request works correctly
- [ ] Push notifications are received when app is in background
- [ ] Push notifications are received when app is closed
- [ ] Notification tap opens relevant app section
- [ ] Error notifications display correctly
- [ ] Resource warning notifications display correctly

## Resource Monitoring
- [ ] System correctly detects low filament
- [ ] System correctly detects low disk space
- [ ] System correctly detects high CPU/memory usage
- [ ] System correctly detects hardware errors
- [ ] Dashboard updates in real-time with resource changes

## Performance
- [ ] Initial load time < 3 seconds on 3G
- [ ] Smooth scrolling (60fps)
- [ ] No excessive memory usage
- [ ] Lighthouse PWA score > 90

## Browser Compatibility
- [ ] Works in Chrome (Android, Desktop)
- [ ] Works in Safari (iOS, MacOS)
- [ ] Works in Firefox
- [ ] Works in Edge

## Device Testing Matrix
| Device | OS | Browser | Installation | Offline | Notifications | Notes |
|--------|----|---------|--------------|---------|--------------| ------|
| iPhone 13 | iOS 15 | Safari | | | | |
| Pixel 6 | Android 12 | Chrome | | | | |
| iPad Pro | iOS 15 | Safari | | | | |
| Samsung Galaxy | Android 11 | Samsung Internet | | | | |
| Desktop | Windows 11 | Chrome | | | | |
| Desktop | macOS | Safari | | | | | 