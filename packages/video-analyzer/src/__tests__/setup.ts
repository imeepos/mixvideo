/**
 * Jest setup file for video analyzer tests
 */

// Mock HTMLVideoElement
Object.defineProperty(HTMLVideoElement.prototype, 'load', {
  writable: true,
  value: jest.fn(),
});

Object.defineProperty(HTMLVideoElement.prototype, 'play', {
  writable: true,
  value: jest.fn().mockResolvedValue(undefined),
});

Object.defineProperty(HTMLVideoElement.prototype, 'pause', {
  writable: true,
  value: jest.fn(),
});

// Mock video properties
Object.defineProperty(HTMLVideoElement.prototype, 'duration', {
  writable: true,
  value: 10,
});

Object.defineProperty(HTMLVideoElement.prototype, 'videoWidth', {
  writable: true,
  value: 1920,
});

Object.defineProperty(HTMLVideoElement.prototype, 'videoHeight', {
  writable: true,
  value: 1080,
});

Object.defineProperty(HTMLVideoElement.prototype, 'currentTime', {
  writable: true,
  value: 0,
});

// Mock HTMLCanvasElement
Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  writable: true,
  value: jest.fn().mockReturnValue({
    drawImage: jest.fn(),
    getImageData: jest.fn(),
    putImageData: jest.fn(),
    createImageData: jest.fn(),
    setTransform: jest.fn(),
    resetTransform: jest.fn(),
    scale: jest.fn(),
    rotate: jest.fn(),
    translate: jest.fn(),
    transform: jest.fn(),
    fillRect: jest.fn(),
    clearRect: jest.fn(),
    strokeRect: jest.fn(),
    fillText: jest.fn(),
    strokeText: jest.fn(),
    measureText: jest.fn().mockReturnValue({ width: 0 }),
    beginPath: jest.fn(),
    closePath: jest.fn(),
    moveTo: jest.fn(),
    lineTo: jest.fn(),
    arc: jest.fn(),
    arcTo: jest.fn(),
    quadraticCurveTo: jest.fn(),
    bezierCurveTo: jest.fn(),
    rect: jest.fn(),
    fill: jest.fn(),
    stroke: jest.fn(),
    clip: jest.fn(),
    save: jest.fn(),
    restore: jest.fn(),
  }),
});

Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
  writable: true,
  value: jest.fn().mockReturnValue('data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD'),
});

// Mock URL.createObjectURL
Object.defineProperty(URL, 'createObjectURL', {
  writable: true,
  value: jest.fn().mockReturnValue('blob:mock-url'),
});

Object.defineProperty(URL, 'revokeObjectURL', {
  writable: true,
  value: jest.fn(),
});

// Mock File API
global.File = class MockFile {
  constructor(bits: any[], filename: string, options: any = {}) {
    this.name = filename;
    this.size = bits.reduce((acc, bit) => acc + (bit.length || 0), 0);
    this.type = options.type || '';
    this.lastModified = options.lastModified || Date.now();
  }
  
  name: string;
  size: number;
  type: string;
  lastModified: number;
} as any;

// Mock Blob
global.Blob = class MockBlob {
  constructor(bits: any[] = [], options: any = {}) {
    this.size = bits.reduce((acc, bit) => acc + (bit.length || 0), 0);
    this.type = options.type || '';
  }
  
  size: number;
  type: string;
} as any;

// Mock fetch for API calls
global.fetch = jest.fn().mockResolvedValue({
  ok: true,
  status: 200,
  json: jest.fn().mockResolvedValue({}),
  text: jest.fn().mockResolvedValue(''),
  blob: jest.fn().mockResolvedValue(new Blob()),
});

// Suppress console warnings in tests
const originalWarn = console.warn;
console.warn = (...args: any[]) => {
  if (args[0]?.includes?.('deprecated')) {
    return;
  }
  originalWarn(...args);
};

// Set test environment variables
process.env.NODE_ENV = 'test';

// Add a dummy test to prevent Jest from complaining
describe('Setup', () => {
  it('should setup test environment', () => {
    expect(true).toBe(true);
  });
});
