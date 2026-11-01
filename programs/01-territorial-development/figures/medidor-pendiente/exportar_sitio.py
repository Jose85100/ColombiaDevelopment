"""Convierte medidor-pendiente.html (generado por build.mjs) en archivos para el sitio:
CSS y JS externos (sin código en línea, por la política de seguridad) y un fragmento de marcado."""
import re,sys,os
SITE=sys.argv[1]
s=open('medidor-pendiente.html').read()

# ---- CSS ----
css=''.join(re.findall(r'<style[^>]*>(.*?)</style>',s,re.S))
def rules(text):
    out=[];i=0;n=len(text)
    while i<n:
        j=text.find('{',i)
        if j<0: break
        sel=text[i:j].strip();d=1;k=j+1
        while k<n and d:
            d+= (text[k]=='{')-(text[k]=='}'); k+=1
        out.append((sel,text[j+1:k-1]));i=k
    return out
LIGHT='[data-theme="light"]'
claro=[];resto=[]
for sel,body in rules(css):
    if sel.startswith('@'): resto.append(f'{sel}{{{body}}}'); continue
    if sel in ('*','html') or sel.startswith('body'): continue          # reglas de página: las del sitio mandan
    if LIGHT in sel: claro.append((sel,body)); continue
    resto.append(f'{sel}{{{body}}}')
tema=[]
for sel,body in claro:
    sel=sel.replace('.iso'+LIGHT,'.fig-iso')
    tema.append(f':root[data-theme="light"] {sel}{{{body}}}')
    tema.append(f'@media (prefers-color-scheme:light){{:root:not([data-theme="dark"]) {sel}{{{body}}}}}')
extra='''.fig-iso{max-width:760px;margin:28px 0 8px}
.fig-iso .iso-figure{margin:0}
.iso-line.fig-aguja{stroke-width:1.1}
.iso-line.fig-marca-limite{stroke-width:1.8}
.iso-halo.fig-halo-suave{filter:blur(4px)}
.proy-intro#ilustracion{margin-top:56px}'''
open(f'{SITE}/proyectos/figuras/medidor-pendiente.css','w').write('/* Generado con la skill Anatomy (MIT) a partir de build.mjs; no editar a mano. */\n'+'\n'.join(resto+tema)+'\n'+extra+'\n')

# ---- JS (módulos, ámbito propio) ----
js='\n'.join(re.findall(r'<script type="module">(.*?)</script>',s,re.S))
open(f'{SITE}/proyectos/figuras/medidor-pendiente.js','w').write('// Generado con la skill Anatomy (MIT) a partir de build.mjs; no editar a mano.\n'+js+'\n')

# ---- marcado ----
m=re.search(r'<figure class="iso-figure">.*?</figure>',s,re.S).group(0)
m=re.sub(r'class="iso-halo"([^>]*?)\s*style="filter:blur\(4px\)"',r'class="iso-halo fig-halo-suave"\1',m)
m=m.replace('class="iso-line" data-tone="hi" d=','class="iso-line fig-marca-limite" data-tone="hi" d=')
m=re.sub(r'(class="iso-line)(" data-tone="lit" data-free="start" d="[^"]*")\s*style="stroke-width:1.1"',r'\1 fig-aguja\2',m)
m=re.sub(r'\sstyle="stroke-width:1.8"','',m)
assert 'style="' not in m, re.findall(r'style="[^"]*"',m)
open('fragmento.html','w').write('<div class="iso fig-iso" id="figura-pendiente">'+m+'</div>\n')
print("css",len(resto),"reglas;",len(tema),"de tema | js",len(js),"bytes | marcado",len(m),"bytes")
