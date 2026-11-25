import packets.Packet;
import packets.PacketType;
import packets.data.GroundTileData;
import packets.data.ObjectData;
import packets.data.ObjectStatusData;
import packets.data.StatData;
import packets.data.WorldPosData;
import packets.incoming.*;
import packets.outgoing.PlayerShootPacket;
import packets.packetcapture.PacketProcessor;
import packets.packetcapture.register.Register;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Base64;
import java.util.Date;
import java.util.Map;
import java.util.TreeMap;

/**
 * Map collector. Uses the RealmShark library to read game packets.
 * It writes one .jsonl file for each map the client enters.
 *
 * Line 1  : {"kind":"mapinfo", ...}  map name, size, seed, raw payload (base64)
 * Line 2+ : {"kind":"update", ...}   new tiles [x,y,type], new objects [id,type,x,y], raw payload
 *
 * The collector does not send, block or change any packet.
 */
public class MapCollector {
    private static final Object LOCK = new Object();
    private static BufferedWriter out;
    private static BufferedWriter ev;          // events file, same name with .events.jsonl
    private static long evCount;
    private static File outFile;
    private static int updates, tiles, objs;
    private static final Map<String, Integer> seen = new TreeMap<>();

    public static void main(String[] args) throws Exception {
        File dir = new File(args.length > 0 ? args[0] : "captures");
        dir.mkdirs();

        Register.INSTANCE.register(PacketType.MAPINFO, p -> onMapInfo(dir, (MapInfoPacket) p));
        Register.INSTANCE.register(PacketType.UPDATE, p -> onUpdate((UpdatePacket) p));
        Register.INSTANCE.registerAll(MapCollector::count);

        // Behaviour events (written to the .events.jsonl file of the current map)
        Register.INSTANCE.register(PacketType.NEWTICK, p -> onTick((NewTickPacket) p));
        Register.INSTANCE.register(PacketType.ENEMYSHOOT, p -> onEnemyShoot((EnemyShootPacket) p));
        Register.INSTANCE.register(PacketType.DAMAGE, p -> onDamage((DamagePacket) p));
        Register.INSTANCE.register(PacketType.AOE, p -> onAoe((AoePacket) p));
        Register.INSTANCE.register(PacketType.SHOWEFFECT, p -> onEffect((ShowEffectPacket) p));
        Register.INSTANCE.register(PacketType.TEXT, p -> onText((TextPacket) p));
        Register.INSTANCE.register(PacketType.NOTIFICATION, p -> onNotification((NotificationPacket) p));
        Register.INSTANCE.register(PacketType.GOTO, p -> onGoto((GotoPacket) p));
        Register.INSTANCE.register(PacketType.QUESTOBJID, p -> onQuest((QuestObjectIdPacket) p));
        Register.INSTANCE.register(PacketType.CREATE_SUCCESS, p -> onCreate((CreateSuccessPacket) p));
        Register.INSTANCE.register(PacketType.PLAYERSHOOT, p -> onPlayerShoot((PlayerShootPacket) p));

        Runtime.getRuntime().addShutdownHook(new Thread(MapCollector::closeFile));

        System.out.println("Map collector started. Capture folder: " + dir.getAbsolutePath());
        System.out.println("Start or restart the game client now. Press Ctrl+C to stop.");
        PacketProcessor processor = new PacketProcessor();
        processor.start();

        long last = System.currentTimeMillis();
        while (true) {
            Thread.sleep(10000);
            synchronized (LOCK) {
                System.out.println("[status] file=" + (outFile == null ? "none" : outFile.getName())
                        + " updates=" + updates + " tiles=" + tiles + " objects=" + objs
                        + " events=" + evCount + " packetTypes=" + seen.size());
            }
        }
    }

    private static void count(Packet p) {
        synchronized (LOCK) {
            seen.merge(p.getClass().getSimpleName(), 1, Integer::sum);
        }
    }

    private static String b64(byte[] data) {
        return data == null ? "" : Base64.getEncoder().encodeToString(data);
    }

    private static String q(String s) {
        if (s == null) return "null";
        StringBuilder sb = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            if (c == '"' || c == '\\') sb.append('\\').append(c);
            else if (c < 32) sb.append(String.format("\\u%04x", (int) c));
            else sb.append(c);
        }
        return sb.append('"').toString();
    }

    /** Maps that are not dungeons. The collector writes no file for them. Add more names here. */
    private static final java.util.Set<String> SKIP = new java.util.HashSet<>(java.util.Arrays.asList(
            "Nexus", "Realm of the Mad God"));

    private static void onMapInfo(File dir, MapInfoPacket m) {
        synchronized (LOCK) {
            closeFile();
            if (m.name != null && SKIP.contains(m.name)) {
                System.out.println("[skip] " + m.name + " is not a dungeon. No file written.");
                return;
            }
            try {
                String safe = (m.name == null ? "unknown" : m.name).replaceAll("[^A-Za-z0-9_.-]", "_");
                String stamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
                outFile = new File(dir, stamp + "_" + safe + ".jsonl");
                out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(outFile), StandardCharsets.UTF_8));
                updates = tiles = objs = 0;
                evCount = 0;
                ev = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(
                        new File(dir, outFile.getName().replace(".jsonl", ".events.jsonl"))), StandardCharsets.UTF_8));
                StringBuilder sb = new StringBuilder();
                sb.append("{\"kind\":\"mapinfo\",\"time\":").append(System.currentTimeMillis())
                        .append(",\"width\":").append(m.width)
                        .append(",\"height\":").append(m.height)
                        .append(",\"name\":").append(q(m.name))
                        .append(",\"displayName\":").append(q(m.displayName))
                        .append(",\"realmName\":").append(q(m.realmName))
                        .append(",\"seed\":").append(m.fp)
                        .append(",\"background\":").append(m.background)
                        .append(",\"difficulty\":").append(m.difficulty)
                        .append(",\"viewDistance\":").append(m.viewDistance)
                        .append(",\"version\":").append(q(m.versionNumber))
                        .append(",\"modifiers\":[").append(q(m.dungeonModifiers)).append(',').append(q(m.dungeonModifiers2))
                        .append(',').append(q(m.dungeonModifiers3)).append(',').append(q(m.dungeonModifiers4)).append(']')
                        .append(",\"grade\":").append(q(m.dungeonGrade))
                        .append(",\"raw\":\"").append(b64(m.getPayload())).append("\"}");
                out.write(sb.toString());
                out.newLine();
                out.flush();
                System.out.println("[map] " + m.name + " (" + m.width + "x" + m.height + ") seed=" + m.fp + " -> " + outFile.getName());
            } catch (Exception e) {
                e.printStackTrace();
                out = null;
            }
        }
    }

    private static void onUpdate(UpdatePacket u) {
        synchronized (LOCK) {
            if (out == null) return;
            try {
                StringBuilder sb = new StringBuilder();
                sb.append("{\"kind\":\"update\",\"time\":").append(System.currentTimeMillis());
                if (u.pos != null) sb.append(",\"pos\":[").append(u.pos.x).append(',').append(u.pos.y).append(']');
                sb.append(",\"tiles\":[");
                for (int i = 0; i < u.tiles.length; i++) {
                    GroundTileData t = u.tiles[i];
                    if (i > 0) sb.append(',');
                    sb.append('[').append(t.x).append(',').append(t.y).append(',').append(t.type).append(']');
                }
                sb.append("],\"objs\":[");
                for (int i = 0; i < u.newObjects.length; i++) {
                    ObjectData o = u.newObjects[i];
                    if (i > 0) sb.append(',');
                    float x = o.status != null && o.status.pos != null ? o.status.pos.x : -1;
                    float y = o.status != null && o.status.pos != null ? o.status.pos.y : -1;
                    int id = o.status != null ? o.status.objectId : -1;
                    sb.append('[').append(id).append(',').append(o.objectType).append(',').append(x).append(',').append(y).append(']');
                }
                sb.append("],\"drops\":").append(u.drops.length);
                sb.append(",\"raw\":\"").append(b64(u.getPayload())).append("\"}");
                out.write(sb.toString());
                out.newLine();
                out.flush();
                onUpdateEvent(u);
                updates++;
                tiles += u.tiles.length;
                objs += u.newObjects.length;
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    // ---------- behaviour events ----------
    // Each event is one JSON line in <capture>.events.jsonl. Field "t" is local time in ms.

    private static void event(String json) {
        // caller holds LOCK
        if (ev == null) return;
        try {
            ev.write(json);
            ev.newLine();
            ev.flush();
            evCount++;
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static String pos(WorldPosData p) {
        return p == null ? "null" : "[" + p.x + "," + p.y + "]";
    }

    /** Stats as [[statNumber, value], ...]. A text stat has a string value. */
    private static void stats(StringBuilder sb, StatData[] st) {
        sb.append('[');
        if (st != null) {
            for (int i = 0; i < st.length; i++) {
                StatData d = st[i];
                if (i > 0) sb.append(',');
                sb.append('[').append(d.statTypeNum).append(',');
                if (d.stringStatValue != null) sb.append(q(d.stringStatValue));
                else sb.append(d.statValue);
                sb.append(']');
            }
        }
        sb.append(']');
    }

    private static void status(StringBuilder sb, ObjectStatusData o) {
        sb.append('[').append(o.objectId).append(',');
        if (o.pos != null) sb.append(o.pos.x).append(',').append(o.pos.y);
        else sb.append("null,null");
        sb.append(',');
        stats(sb, o.stats);
        sb.append(']');
    }

    private static void onTick(NewTickPacket t) {
        synchronized (LOCK) {
            if (ev == null) return;
            StringBuilder sb = new StringBuilder();
            sb.append("{\"k\":\"tick\",\"t\":").append(System.currentTimeMillis())
                    .append(",\"id\":").append(t.tickId)
                    .append(",\"srv\":").append(t.serverRealTimeMS)
                    .append(",\"dt\":").append(t.tickTime)
                    .append(",\"s\":[");
            if (t.status != null) {
                for (int i = 0; i < t.status.length; i++) {
                    if (i > 0) sb.append(',');
                    status(sb, t.status[i]);
                }
            }
            sb.append("]}");
            event(sb.toString());
        }
    }

    /** New objects with their first stats (HP, loot bag items, portal names) and dropped object ids. */
    private static void onUpdateEvent(UpdatePacket u) {
        // caller holds LOCK
        if (ev == null) return;
        StringBuilder sb = new StringBuilder();
        sb.append("{\"k\":\"upd\",\"t\":").append(System.currentTimeMillis()).append(",\"new\":[");
        for (int i = 0; i < u.newObjects.length; i++) {
            ObjectData o = u.newObjects[i];
            if (i > 0) sb.append(',');
            sb.append('[').append(o.status != null ? o.status.objectId : -1).append(',').append(o.objectType).append(',');
            if (o.status != null && o.status.pos != null) sb.append(o.status.pos.x).append(',').append(o.status.pos.y);
            else sb.append("null,null");
            sb.append(',');
            stats(sb, o.status != null ? o.status.stats : null);
            sb.append(']');
        }
        sb.append("],\"drop\":[");
        for (int i = 0; i < u.drops.length; i++) {
            if (i > 0) sb.append(',');
            sb.append(u.drops[i]);
        }
        sb.append("]}");
        event(sb.toString());
    }

    private static void onEnemyShoot(EnemyShootPacket e) {
        synchronized (LOCK) {
            event("{\"k\":\"eshoot\",\"t\":" + System.currentTimeMillis() + ",\"owner\":" + e.ownerId
                    + ",\"bid\":" + e.bulletId + ",\"btype\":" + e.bulletType + ",\"pos\":" + pos(e.startingPos)
                    + ",\"ang\":" + e.angle + ",\"dmg\":" + e.damage + ",\"n\":" + e.numShots + ",\"inc\":" + e.angleInc + "}");
        }
    }

    private static void onDamage(DamagePacket d) {
        synchronized (LOCK) {
            StringBuilder sb = new StringBuilder();
            sb.append("{\"k\":\"dmg\",\"t\":").append(System.currentTimeMillis()).append(",\"target\":").append(d.targetId)
                    .append(",\"amt\":").append(d.damageAmount).append(",\"bid\":").append(d.bulletId)
                    .append(",\"src\":").append(d.objectId).append(",\"fx\":[");
            if (d.effects != null) for (int i = 0; i < d.effects.length; i++) {
                if (i > 0) sb.append(',');
                sb.append(d.effects[i]);
            }
            sb.append("]}");
            event(sb.toString());
        }
    }

    private static void onAoe(AoePacket a) {
        synchronized (LOCK) {
            event("{\"k\":\"aoe\",\"t\":" + System.currentTimeMillis() + ",\"pos\":" + pos(a.pos) + ",\"r\":" + a.radius
                    + ",\"dmg\":" + a.damage + ",\"fx\":" + a.effect + ",\"dur\":" + a.duration + ",\"orig\":" + a.origType
                    + ",\"ap\":" + a.armorPiercing + "}");
        }
    }

    private static void onEffect(ShowEffectPacket f) {
        synchronized (LOCK) {
            event("{\"k\":\"fx\",\"t\":" + System.currentTimeMillis() + ",\"type\":" + f.effectType + ",\"target\":" + f.targetObjectId
                    + ",\"p1\":" + pos(f.pos1) + ",\"p2\":" + pos(f.pos2) + ",\"color\":" + f.color + ",\"dur\":" + f.duration + "}");
        }
    }

    private static void onText(TextPacket x) {
        synchronized (LOCK) {
            event("{\"k\":\"text\",\"t\":" + System.currentTimeMillis() + ",\"obj\":" + x.objectId + ",\"name\":" + q(x.name)
                    + ",\"text\":" + q(x.text) + "}");
        }
    }

    private static void onNotification(NotificationPacket n) {
        synchronized (LOCK) {
            event("{\"k\":\"notif\",\"t\":" + System.currentTimeMillis() + ",\"obj\":" + n.objectId + ",\"msg\":" + q(n.message)
                    + ",\"effect\":" + q(String.valueOf(n.effect)) + "}");
        }
    }

    private static void onGoto(GotoPacket g) {
        synchronized (LOCK) {
            event("{\"k\":\"goto\",\"t\":" + System.currentTimeMillis() + ",\"obj\":" + g.objectId + ",\"pos\":" + pos(g.position) + "}");
        }
    }

    private static void onQuest(QuestObjectIdPacket qp) {
        synchronized (LOCK) {
            StringBuilder sb = new StringBuilder("{\"k\":\"quest\",\"t\":" + System.currentTimeMillis() + ",\"obj\":" + qp.objectId + ",\"list\":[");
            if (qp.list != null) for (int i = 0; i < qp.list.length; i++) {
                if (i > 0) sb.append(',');
                sb.append(qp.list[i]);
            }
            sb.append("]}");
            event(sb.toString());
        }
    }

    private static void onCreate(CreateSuccessPacket c) {
        synchronized (LOCK) {
            event("{\"k\":\"self\",\"t\":" + System.currentTimeMillis() + ",\"obj\":" + c.objectId + ",\"char\":" + c.charId + "}");
        }
    }

    private static void onPlayerShoot(PlayerShootPacket p) {
        synchronized (LOCK) {
            event("{\"k\":\"pshoot\",\"t\":" + System.currentTimeMillis() + ",\"weapon\":" + p.weaponId + ",\"ang\":" + p.angle
                    + ",\"pos\":" + pos(p.startingPos) + ",\"ppos\":" + pos(p.playerPosition) + "}");
        }
    }

    private static void closeFile() {
        synchronized (LOCK) {
            if (out != null) {
                try {
                    out.close();
                } catch (Exception ignored) {
                }
                System.out.println("[closed] " + outFile.getName() + " updates=" + updates + " tiles=" + tiles
                        + " objects=" + objs + " events=" + evCount);
                out = null;
            }
            if (ev != null) {
                try {
                    ev.close();
                } catch (Exception ignored) {
                }
                ev = null;
            }
        }
    }
}
