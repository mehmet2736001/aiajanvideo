import { loadFont as loadCinzel } from '@remotion/google-fonts/Cinzel';
import { loadFont as loadCormorant } from '@remotion/google-fonts/CormorantGaramond';

// Fontlar render sırasında bir kez yüklenir. Cinzel'de bulunmayan Türkçe harfler için
// Cormorant Garamond yedek olarak zincire eklenir (glif bazında devreye girer).
const cinzel = loadCinzel();
const cormorant = loadCormorant();

export const SERIF = `${cinzel.fontFamily}, ${cormorant.fontFamily}, Georgia, serif`;
