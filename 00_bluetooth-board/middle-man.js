const noble = require('noble');

// Replace 'your_device_mac_address' with the actual MAC address of your ESP32 device.
const esp32MacAddress = '40:91:51:FD:21:A6';

noble.on('stateChange', (state) => {
  if (state === 'poweredOn') {
    noble.startScanning([], true);
  } else {
    noble.stopScanning();
  }
});

noble.on('discover', (peripheral) => {
  if (peripheral.address === esp32MacAddress) {
    noble.stopScanning(); // Stop scanning once the target device is found.

    peripheral.connect((err) => {
      if (!err) {
        peripheral.on('disconnect', () => {
          console.log('Disconnected from the device.');
          process.exit(0);
        });

        peripheral.discoverAllServicesAndCharacteristics((err, services, characteristics) => {
          if (!err) {
            // You can work with services and characteristics here.
            console.log('Connected to the device.');
          }
        });
      }
    });
  }
});
