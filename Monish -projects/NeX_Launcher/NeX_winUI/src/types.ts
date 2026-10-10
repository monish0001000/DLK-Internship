export type AppID =
  | 'edge'
  | 'word'
  | 'excel'
  | 'pdf'
  | 'notepad'
  | 'calculator'
  | 'paint'
  | 'files'
  | 'camera'
  | 'settings';

export interface AppDefinition {
  id: AppID;
  name: string;
  iconName: string;
  bgClass: string;
  iconColorClass: string;
  description: string;
}

export interface VirtualFile {
  name: string;
  type: 'doc' | 'sheet' | 'pdf' | 'text' | 'image';
  content: string;
  size: string;
  updatedAt: string;
}

export interface SystemState {
  mode: 'Mode 1' | 'Mode 2' | 'Admin Mode';
  isOnline: boolean;
  isMuted: boolean;
  volume: number;
  wifiConnected: boolean;
  integritySecure: boolean;
  logs: string[];
  theme: 'light' | 'dark';
}
