"""Build a PSP PES 2013 option file from the preserved Argentine PES 2012 save.

Uses the MIT-licensed PES_WE_11_14_OF_Editor for format definitions. Does not
modify either input. Run with ../tools/venv/bin/python.
"""
import json
import struct
import sys
from collections import deque
from pathlib import Path
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
EDITOR = ROOT / 'tools/pes-of-editor'
sys.path.insert(0, str(EDITOR))
from editor.images import PNG
PNG.png_bytes_to_tk_img = lambda self: None  # headless: no Tk presentation
from editor.option_file import OptionFile
from editor.player import Player
from editor.logo import Logo
from editor.kits import Kits

def load(year):
    config = 'PES 2012 PSP ULES01542.yaml' if year == 2012 else 'PES 2013 PSP ULES01580.yaml'
    return OptionFile(ROOT / 'conversion' / f'{year}-decrypted.bin',
                      yaml.safe_load((EDITOR / 'config/PSP' / config).read_text()))

# Twenty first-division slots: River and Quilmes replace the relegated Banfield
# and Olimpo. Keep those two clubs, Instituto and Rosario Central as extras.
source_clubs = [20,21,22,23,25,26,27,28,29,30,31,32,129,34,130,35,36,37,38,39,24,33,131,132]
dest_clubs = list(range(20,40)) + list(range(126,130))
source = load(2012)
peru_team = source.teams[50]
peru_kits = bytes(source.data[peru_team.kits.address:peru_team.kits.address+352])
# The supplied USA game's fresh defaults render Argentina in yellow/cyan and
# Brazil in green. Keep their rosters; import only the four editable kits from
# the Argentine option file, whose colors were verified in RetroArch.
national_kits = {
    i: bytes(source.data[source.teams[i].kits.address:
                         source.teams[i].kits.address+352])
    for i in (44, 45)
}
snapshots = []
player_data = {}
for ci in source_clubs:
    team = source.teams[75 + ci]
    players = []
    for p in team.players:
        if p is None:
            players.append(0)
        else:
            players.append(p.idx)
            player_data[p.idx] = (p.name, bytes(source.data[p.address:p.address+124]))
    snapshots.append(dict(name=source.clubs[ci].name,
        club=bytes(source.data[source.clubs[ci].name_address:source.clubs[ci].name_address+88]),
        kits=bytes(source.data[team.kits.address:team.kits.address+648]),
        formation=bytes(source.data[team.formation.address:team.formation.address+364]),
        dorsals=bytes(source.data[team.dorsal_address:team.dorsal_address+32]),
        players=players))
logos = bytes(source.data[Logo.start_address:Logo.start_address+Logo.total*Logo.size])
extra_images = bytes(source.data[source.of_block[8]:source.of_block[8]+source.of_block_size[8]])
extra_images = bytearray(extra_images)
# The PSP games have 30 high-resolution / 60 low-resolution custom emblem slots.
# The 2013 stock emblem table has five fewer entries than the 2012 table.
for i in range(90):
    loc=extra_images[6+i]
    if loc==93: continue
    if loc < 30: off=104+loc*5184
    else:
        slot=loc-30;off=104+(29-slot//2)*5184+(slot%2)*2176
    struct.pack_into('<I',extra_images,off+4,349+i)

def replace_badge(old_id,filename):
    loc=extra_images[6+old_id-354]-30
    off=104+(29-loc//2)*5184+(loc%2)*2176
    im=Image.open(ROOT/'conversion'/filename).convert('RGBA')
    # Remove the baked-in pale checkerboard outside the shield. Flooding from
    # the border preserves River's white interior behind its black outline.
    px=im.load();seen=set();todo=deque()
    for x in range(im.width): todo.extend([(x,0),(x,im.height-1)])
    for y in range(im.height): todo.extend([(0,y),(im.width-1,y)])
    while todo:
        x,y=todo.popleft()
        if (x,y) in seen or not (0<=x<im.width and 0<=y<im.height): continue
        seen.add((x,y));r,g,b,a=px[x,y]
        if a==0 or (min(r,g,b)>175 and max(r,g,b)-min(r,g,b)<35):
            px[x,y]=(0,0,0,0)
            todo.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
    im=im.crop(im.getbbox())
    im.save(ROOT/'conversion'/filename.replace('.png','-clean.png'))
    im.thumbnail((60,60),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(64,64));canvas.alpha_composite(im,((64-im.width)//2,(64-im.height)//2))
    q=canvas.quantize(colors=16,method=Image.Quantize.FASTOCTREE)
    pal=q.getpalette('RGBA')[:64]
    extra_images[off+64:off+128]=bytes(pal)
    px=list(q.getdata());packed=bytes((px[i]<<4)|px[i+1] for i in range(0,len(px),2))
    extra_images[off+128:off+2176]=packed

replace_badge(443,'boca.png')
replace_badge(438,'river.png')

# Classes use global offsets, so only inspect source objects before loading dest.
dest = load(2013)
for i, kits in national_kits.items():
    address = dest.teams[i].kits.address
    dest.data[address:address+352] = kits
    for k in range(4):
        struct.pack_into('<H', dest.data, address+k*88+80, 65535)
protected_ids = set()
for ti, team in enumerate(dest.teams):
    if ti not in {75+i for i in dest_clubs}:
        protected_ids.update(p.idx for p in team.players if p)
available = [p.idx for p in dest.players if p.idx > 0 and p.idx not in protected_ids
             and p.idx < Player.first_ml_default]
# Empty edit-player slots are referenced by the stock file's placeholder edit
# teams, but contain no user-created players. Use them for the remaining players.
available += [32768+i for i in range(Player.total_edit)
              if not bytes(dest.data[Player.start_address_edited+i*124:
                                     Player.start_address_edited+i*124+32]).strip(b'\x00')]
assert len(available) >= len(player_data), (len(available), len(player_data))
mapping = dict(zip(sorted(player_data), available))
for old_id, new_id in mapping.items():
    p = dest.get_player_by_idx(new_id)
    dest.data[p.address:p.address+124] = player_data[old_id][1]
    p.init_stats()
    for flag in p.edited_flags:
        flag.set_value(1)
    # Disable mismatched commentary callnames across yearly databases.
    p.callname.set_value(65535)

report = []
for ci, data in zip(dest_clubs, snapshots):
    c, t = dest.clubs[ci], dest.teams[75+ci]
    dest.data[c.name_address:c.name_address+88] = data['club']
    dest.data[c.name_address+56] = 1  # PSP name-edited flag
    emblem=struct.unpack_from('<I',data['club'],60)[0]
    if emblem==273: emblem=443  # Boca's former built-in emblem
    if emblem==274: emblem=438  # River's former built-in emblem
    if emblem >=354: emblem-=5
    struct.pack_into('<II',dest.data,c.name_address+60,emblem,emblem)
    dest.data[c.name_address+68:c.name_address+70]=b'\x01\x01'
    # Stadium numbering differs. Pick a valid PES 2013 stadium.
    dest.data[c.name_address+81] = 0
    dest.data[c.name_address+83] = 1
    dest.data[t.kits.address:t.kits.address+648] = data['kits']
    if data['name'] == 'RIVER PLATE':
        # Peru supplies the game's editable white/red diagonal template.
        # Kit order is goalkeeper 1, outfield 1, goalkeeper 2, outfield 2.
        for k in range(4):
            a=t.kits.address+k*88
            dest.data[a:a+88]=peru_kits[k*88:k*88+88]
            dest.data[a+58]=0  # clubs do not use a front shirt number
            if k==1:
                for off,value in [(10,0x8000),(12,0x8000),(14,0xffff),(16,0x8000),
                                  (18,0xffff),(20,0x9496),(22,0x9496)]:
                    struct.pack_into('<H',dest.data,a+off,value)
    for k in range(4):
        dest.data[t.kits.address+k*88+80:t.kits.address+k*88+82]=b'\xff\xff'
    dest.data[t.formation.address:t.formation.address+364] = data['formation']
    dest.data[t.dorsal_address:t.dorsal_address+32] = data['dorsals']
    ids = [mapping.get(i,0) for i in data['players']]
    dest.data[t.address:t.address+64] = struct.pack('<32H',*ids)
    report.append(dict(club=data['name'],slot=ci,
                       players=[player_data[i][0] for i in data['players'] if i]))

dest.data[Logo.start_address:Logo.start_address+len(logos)] = logos
dest.data[dest.of_block[8]:dest.of_block[8]+len(extra_images)] = extra_images
for league in dest.leagues:
    if 'LIGUE' in league.name.upper() or 'FRANCE' in league.name.upper():
        league.set_name('Liga Argentina')

# Preference bytes confirmed by the game's own Spanish Latin American save.
dest.data[5910] = 4  # Spanish event tables for the Closs audio bank
dest.data[5957] = 11  # Spanish Latin American menu text

assert len(dest.data) == dest.of_byte_length
(ROOT/'conversion/argentina-2013-decrypted.bin').write_bytes(dest.data)
(ROOT/'conversion/rosters.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(f'Converted {len(snapshots)} clubs and {len(player_data)} players; {len(available)} available slots.')
print('All national-team and other-club player IDs preserved.')
