import { formatDuration, validateEmail, Video } from '@mixvideo/shared';

function main() {
  console.log('🎬 MixVideo - TypeScript Monorepo Demo');
  console.log('=====================================');

  const sampleVideo: Video = {
    id: '1',
    title: 'Sample Video',
    url: 'https://example.com/video.mp4',
    duration: 125, // 2:05
    userId: 'user1',
    createdAt: new Date(),
  };

  const email = 'test@example.com';

  console.log('\n📹 Sample Video:');
  console.log(`Title: ${sampleVideo.title}`);
  console.log(`Duration: ${formatDuration(sampleVideo.duration)}`);
  console.log(`Created: ${sampleVideo.createdAt.toLocaleDateString()}`);

  console.log('\n📧 Email Validation:');
  console.log(`Email: ${email}`);
  console.log(`Valid: ${validateEmail(email) ? 'Yes' : 'No'}`);

  console.log('\n✅ Shared package integration working correctly!');
}

if (require.main === module) {
  main();
}
