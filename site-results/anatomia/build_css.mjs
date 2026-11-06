// Genera out/anatomia.css: el CSS del kit de Anatomy (MIT) atado al tema del sitio.
// Oscuro por defecto; claro con data-theme="light" o con prefers-color-scheme: light sin elección guardada (como tema.js).
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ISO_CSS } from './kit/iso-kit.mjs';
const HERE = dirname(fileURLToPath(import.meta.url));
const light = ISO_CSS.match(/\.iso\[data-theme="light"\]\{([\s\S]*?)\n\}/)[1];
const rest = ISO_CSS.replace(/\.iso\[data-theme="light"\]\{[\s\S]*?\n\}/, '');
const css = `/* Figuras isométricas. Basado en Anatomy (MIT, github.com/wheresryan22/anatomy). Generado por site-results/anatomia/build_css.mjs. */
${rest.trim()}
:root[data-theme="light"] .iso{${light}}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]) .iso{${light}}}
.iso{color:var(--ink)}
.iso-figura{margin:0;padding:6px 0 0}
`;
mkdirSync(join(HERE, 'out'), { recursive: true });
writeFileSync(join(HERE, 'out', 'anatomia.css'), css);
console.log('anatomia.css', css.length);
