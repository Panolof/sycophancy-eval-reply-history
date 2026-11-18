"""Shared palette and SVG primitives for the report figures."""
from html import escape
WHITE = '#ffffff'
GREY = '#dedede'
GROUND = '#eeeeee'
INK = '#263238'
TEAL = '#176b68'
BORDER = '#aab5b5'
FONT = 23
WIDTH = 1300
PLACED_MM = 165.10
BANNED = ('neutral', 'capitulation', 'sycophancy', 'rules out', 'isolates', 'no pressure')
def start(height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" font-family="Arial, sans-serif">', f'<rect width="{WIDTH}" height="{height}" fill="{WHITE}"/>']
def rect(s,x,y,w,h,fill,stroke='none',**attrs):
    extra=' '.join(f'{k.replace("_","-")}="{escape(str(v),quote=True)}"' for k,v in attrs.items())
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" {extra}/>')
def text(s,x,y,value,size=FONT,fill=INK,anchor='start',weight='normal',**attrs):
    extra=' '.join(f'{k.replace("_","-")}="{escape(str(v),quote=True)}"' for k,v in attrs.items())
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{escape(str(value))}</text>')
