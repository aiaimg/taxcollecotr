// Polyfills for Jest environment
if (typeof global.setImmediate === 'undefined') {
  global.setImmediate = (fn, ...args) => global.setTimeout(fn, 0, ...args);
}
if (typeof global.clearImmediate === 'undefined') {
  global.clearImmediate = global.clearTimeout;
}

// Mock global objects that React Native expects
if (typeof global.window === 'undefined') {
  global.window = {};
}
if (typeof global.document === 'undefined') {
  global.document = {};
}
if (typeof global.navigator === 'undefined') {
  global.navigator = {};
}
