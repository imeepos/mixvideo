// Shared types
export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

export interface Video {
  id: string;
  title: string;
  url: string;
  duration: number;
  userId: string;
  createdAt: Date;
}

// Shared utilities
export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Constants
export const API_ENDPOINTS = {
  USERS: '/api/users',
  VIDEOS: '/api/videos',
  AUTH: '/api/auth',
} as const;

export const VIDEO_FORMATS = ['mp4', 'webm', 'avi', 'mov'] as const;
export type VideoFormat = (typeof VIDEO_FORMATS)[number];
