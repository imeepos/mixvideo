// Mock implementation for @mixvideo/gemini package

const mockUseGemini = () => ({
  generateContent: jest.fn().mockResolvedValue({
    response: {
      text: () => JSON.stringify({
        summary: 'Mock video analysis',
        scenes: [
          {
            timestamp: 0,
            duration: 10,
            description: 'Mock scene',
            confidence: 0.9
          }
        ],
        objects: [
          {
            name: 'person',
            confidence: 0.8,
            boundingBox: { x: 0, y: 0, width: 100, height: 100 }
          }
        ],
        metadata: {
          duration: 30,
          resolution: '1920x1080',
          fps: 30
        }
      })
    }
  })
});

const mockUploadFileToGemini = jest.fn().mockResolvedValue({
  uri: 'gs://mock-bucket/mock-file.mp4',
  mimeType: 'video/mp4'
});

const mockUseGeminiAccessToken = jest.fn().mockResolvedValue('mock-access-token');

module.exports = {
  useGemini: mockUseGemini,
  uploadFileToGemini: mockUploadFileToGemini,
  useGeminiAccessToken: mockUseGeminiAccessToken
};
