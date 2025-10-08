export interface UploadedFile {
  id: string;
  file: File;
  size: string;
}
export enum ThemeType {
  Light = "light",
  Dark = "dark",
  Custom = "custom",
  Faint_Yellow = "faint_yellow",
  Royal_Blue = "royal_blue",
  Light_Red = "light_red",
  Dark_Pink = "dark_pink",
}

export enum LanguageType {
  // Major World Languages
  //   Auto = "Auto",
  English = "英文",
  ChineseSimplified = "中文",
}

export interface PresentationConfig {
  slides: "2" | "5" | "8" | "10" | "12" | "15" | null;
  language: LanguageType | null;
  prompt: string;
}
