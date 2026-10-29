import { VideoData } from './types';

export const defaultVideoData: VideoData = {
  headerSubtitle: 'Allah kâinatı',
  headerMain: 'NEDEN BİRDEN DEĞİL DE ALTI GÜNDE?',
  circledWord: 'BİRDEN',
  highlightedText: 'ALTI GÜNDE?',
  cards: [
    {
      id: '1',
      label: 'kâinat',
      value: '6 gün',
      icon: 'galaxy',
      color: '#1e3a8a',
    },
    {
      id: '2',
      label: 'anne karnında',
      value: '9 ay',
      icon: 'embryo',
      color: '#15803d',
    },
    {
      id: '3',
      label: 'Kur\'an',
      value: '23 yıl',
      icon: 'book',
      color: '#854d0e',
    },
  ],
  timeline: {
    startYear: '610',
    endYear: '632',
    durationLabel: '23 yıl',
    title: 'Vahiy de böyle geldi',
    ayahArabic: 'لِنُثَبِّتَ بِهِ فُؤَادَكَ',
    ayahTranslation: 'Kalbine iyice yerleşsin diye.',
    ayahRef: 'Furkân 32',
  },
  socialHandle: '@kanitlarla_islam',
  subtitles: [
    { text: 'Allah, kâinatı', start: 0.1, end: 1.2 },
    { text: 'neden birden değil de', start: 1.2, end: 2.5 },
    { text: 'altı günde yarattı?', start: 2.5, end: 4.0 },
    { text: 'Seni de anne karnında', start: 4.0, end: 5.5 },
    { text: 'dokuz ayda yarattı.', start: 5.5, end: 7.2 },
    { text: 'Kur\'an\'ı 23 yılda indirdi.', start: 7.2, end: 9.5 },
    { text: 'Vahiy de böyle geldi.', start: 9.5, end: 11.0 },
    { text: 'Kalbine iyice yerleşsin diye.', start: 11.0, end: 13.5 },
  ],
};
