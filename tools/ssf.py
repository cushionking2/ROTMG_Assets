"""Decoder for the spritesheetf FlatBuffers binary. Use: load() -> dict sheet -> list of sprite dicts."""
import struct
def load(path):
    b = open(path, 'rb').read()
    u32 = lambda o: struct.unpack_from('<I', b, o)[0]
    i32 = lambda o: struct.unpack_from('<i', b, o)[0]
    u16 = lambda o: struct.unpack_from('<H', b, o)[0]
    f32s = lambda o, n: struct.unpack_from('<%df' % n, b, o)
    def tbl(p):
        v = p - i32(p); nf = (u16(v) - 4) // 2
        return [u16(v + 4 + 2 * i) for i in range(nf)]
    root = u32(0); rt = root; offs = tbl(rt)
    a = rt + offs[0]; vec = a + u32(a)
    out = {}
    for k in range(u32(vec)):
        e = vec + 4 + 4 * k; p = e + u32(e); o = tbl(p)
        a = p + o[0]; s = a + u32(a); name = b[s + 4:s + 4 + u32(s)].decode()
        kind = u32(p + o[1])
        a2 = p + o[2]; sv = a2 + u32(a2)
        sprites = []
        for j in range(u32(sv)):
            q = sv + 4 + 4 * j; sp = q + u32(q); so = tbl(sp)
            g = lambda i: sp + so[i] if i < len(so) and so[i] else None
            r = f32s(g(0), 4) if g(0) else None
            sprites.append(dict(index=j, rect=r, f1=u32(g(1)) if g(1) else None, f2=u32(g(2)) if g(2) else None,
                                f3=u32(g(3)) if g(3) else None, color=f32s(g(4), 4) if g(4) else None,
                                f7=u32(g(7)) if g(7) else None))
        out[name] = dict(kind=kind, sprites=sprites)
    return out


def load_frames(path):
    """Second root vector: per-cell records for character sheets. Returns list of dicts in file order."""
    b = open(path, 'rb').read()
    u32 = lambda o: struct.unpack_from('<I', b, o)[0]
    i32 = lambda o: struct.unpack_from('<i', b, o)[0]
    u16 = lambda o: struct.unpack_from('<H', b, o)[0]
    f32s = lambda o, n: struct.unpack_from('<%df' % n, b, o)
    def tbl(p):
        v = p - i32(p); nf = (u16(v) - 4) // 2
        return [u16(v + 4 + 2 * i) for i in range(nf)]
    vec = 0x10 + u32(0x10)
    out = []
    for k in range(u32(vec)):
        e = vec + 4 + 4 * k; p = e + u32(e); o = tbl(p)
        a = p + o[0]; s = a + u32(a); name = b[s + 4:s + 4 + u32(s)].decode()
        f1 = u32(p + o[1]) if o[1] else 0
        f4 = u32(p + o[4]) if o[4] else 0
        a = p + o[5]; t = a + u32(a); to = tbl(t)
        rect = f32s(t + to[0], 4)
        out.append(dict(pos=k, sheet=name, f1=f1, f4=f4, rect=rect,
                        ex=u32(t + to[2]) if to[2] else None, f7=u32(t + to[7]) if to[7] else None,
                        color=f32s(t + to[4], 4) if to[4] else None))
    return out
