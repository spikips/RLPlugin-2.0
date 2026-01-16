package net.runelite.client.plugins.asd;
import net.runelite.api.events.VarbitChanged;
import net.runelite.api.events.VarClientIntChanged;
import com.google.inject.Provides;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldArea;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.events.AnimationChanged;
import net.runelite.api.events.GameTick;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.client.config.ConfigManager;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;
import net.runelite.client.game.ItemManager;
import net.runelite.http.api.item.ItemEquipmentStats;
import net.runelite.client.eventbus.EventBus;
import net.runelite.http.api.item.ItemStats;
import javax.inject.Inject;
import net.runelite.client.ui.overlay.Overlay;
import net.runelite.client.ui.overlay.OverlayManager;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayPriority;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Point;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

@Slf4j
@PluginDescriptor(
        name = ".asd",
        description = "A plugin to extract various game data with configurable toggles",
        tags = {"data", "debug", "extraction", "combat"}
)
public class AsdPlugin extends Plugin {
    @Inject
    private SocketServer socketServer;

    @Inject
    private EventBus eventBus;

    @Inject
    private BankCache bankCache;

    @Inject
    private Client client;

    @Inject
    private AsdConfig config;

    @Inject
    private OverlayManager overlayManager;

    @Inject
    private MainOverlay overlay;

    @Inject
    private NpcOverlay npcLocationOverlay;

    @Inject
    private ItemManager itemManager;

    @Inject
    private ConfigManager configManager;

    @Inject
    private MinimapHoverHandler minimapHoverHandler;

    @Inject
    private MinimapHoverOverlay minimapHoverOverlay;

    @Inject
    private VarbitHandler varbitHandler;

    @Inject
    private PlayerOverlay playerOverlay;

    @Inject
    private CannonHandler cannonHandler;

    @Inject
    private ClickHandler clickHandler;

    protected MenuEntry[] currentMenuEntries;
    protected String playerLocationText;
    protected String skillLevelsText;
    protected String weightText;
    protected String runEnergyText;
    protected String healthText;
    protected String combatStyleText;
    protected String equippedGearText;
    protected String chatMessagesText;
    private WorldPoint referencePosition;
    private boolean underAttack = false;
    private boolean reachableUnderAttack = false;

    private static final int[] DX = {0, 1, 0, -1}; // N, E, S, W
    private static final int[] DY = {1, 0, -1, 0};
    private static final int BLOCK_MOVEMENT_NORTH = CollisionDataFlag.BLOCK_MOVEMENT_NORTH;
    private static final int BLOCK_MOVEMENT_EAST = CollisionDataFlag.BLOCK_MOVEMENT_EAST;
    private static final int BLOCK_MOVEMENT_SOUTH = CollisionDataFlag.BLOCK_MOVEMENT_SOUTH;
    private static final int BLOCK_MOVEMENT_WEST = CollisionDataFlag.BLOCK_MOVEMENT_WEST;
    private static final int BLOCK_MOVEMENT_FULL = CollisionDataFlag.BLOCK_MOVEMENT_FULL;
    private static final int BLOCK_MOVEMENT_OBJECT = CollisionDataFlag.BLOCK_MOVEMENT_OBJECT;
    private static final int BLOCK_MOVEMENT_FLOOR = CollisionDataFlag.BLOCK_MOVEMENT_FLOOR;

    private final HashMap<Integer, Integer> npcLastAttackTicks = new HashMap<>(); // NPC index -> last attack tick
    private final Map<String, List<Integer>> attackAnimsByName = new HashMap<>(); // Lowercase NPC name -> attack animations
    private final Map<String, Integer> cooldownByName = new HashMap<>(); // Lowercase NPC name -> attack cooldown in ticks
    private final List<Map<String, Object>> variableChanges = new ArrayList<>(); // Renamed from varbitChanges    private final Map<Integer, Integer> lastVarbitValues = new HashMap<>();
    private int tickCount = 0; // Game tick counter
    private final Map<Integer, Integer> lastVarpValues = new HashMap<>(); // New: For tracking Varps
    @Provides
    AsdConfig provideConfig(ConfigManager configManager) {
        return configManager.getConfig(AsdConfig.class);
    }
    private final Map<Integer, Integer> lastVarbitValues = new HashMap<>();
    private final Map<Integer, Integer> lastVarClientIntValues = new HashMap<>(); // For VarClientInts (optional, since event provides old value)


    @Override
    protected void startUp() throws Exception {
        log.info("AsdPlugin started!");
        eventBus.register(varbitHandler);
        varbitHandler.updateFilters();
        overlayManager.add(overlay);
        eventBus.register(bankCache);
        overlayManager.add(npcLocationOverlay);
        overlayManager.add(new AsdUnderAttackOverlay(this, config));
        overlayManager.add(new AsdReachableAttackOverlay(this, config));
        socketServer.startServer();
        npcLastAttackTicks.clear();
        attackAnimsByName.clear();
        cooldownByName.clear();
        overlayManager.add(minimapHoverOverlay);
        overlayManager.add(playerOverlay);
        eventBus.register(cannonHandler);
        eventBus.register(clickHandler);
    }

    @Override
    protected void shutDown() throws Exception {
        log.info("AsdPlugin stopped!");
        eventBus.unregister(varbitHandler);
        overlayManager.remove(overlay);
        eventBus.unregister(bankCache);
        overlayManager.remove(npcLocationOverlay);
        overlayManager.removeIf(overlay -> overlay instanceof AsdUnderAttackOverlay);
        overlayManager.removeIf(overlay -> overlay instanceof AsdReachableAttackOverlay);
        socketServer.stopServer();
        playerLocationText = null;
        skillLevelsText = null;
        weightText = null;
        runEnergyText = null;
        healthText = null;
        combatStyleText = null;
        equippedGearText = null;
        chatMessagesText = null;
        currentMenuEntries = null;
        underAttack = false;
        reachableUnderAttack = false;
        npcLastAttackTicks.clear();
        attackAnimsByName.clear();
        cooldownByName.clear();
        overlayManager.remove(minimapHoverOverlay);
        overlayManager.remove(playerOverlay);
        eventBus.unregister(cannonHandler);
        eventBus.unregister(clickHandler);
    }



    @Subscribe
    public void onAnimationChanged(AnimationChanged event) {
        if (event.getActor() instanceof NPC) {
            NPC npc = (NPC) event.getActor();
            if (npc.getInteracting() == client.getLocalPlayer()) {
                int anim = npc.getAnimation();
                String name = npc.getName();
                if (name != null) {
                    String lowerName = name.toLowerCase();
                    if (attackAnimsByName.containsKey(lowerName) && attackAnimsByName.get(lowerName).contains(anim)) {
                        npcLastAttackTicks.put(npc.getIndex(), tickCount);
                        log.info("Detected attack from {} (ID: {}, Anim: {}) at tick {}", name, npc.getId(), anim, tickCount);
                    }
                }
            }
        }
    }

    @Subscribe
    public void onVarbitChanged(VarbitChanged event) {
        if (!config.varbitChangeLogger()) return;

        int newValue = event.getValue();
        Map<String, Object> change = new HashMap<>();
        change.put("old", -1); // Default; override below if tracked
        change.put("new", newValue);
        change.put("tick", client.getTickCount());

        if (event.getVarbitId() == -1) {
            // This is a Varp (Varplayer) change
            int varpId = event.getVarpId();
            Integer oldValue = lastVarpValues.get(varpId);
            if (oldValue != null && oldValue == newValue) return; // No actual change

            change.put("type", "varp");
            change.put("id", varpId);
            change.put("old", oldValue == null ? -1 : oldValue);
            lastVarpValues.put(varpId, newValue);
        } else {
            // This is a Varbit change
            int varbitId = event.getVarbitId();
            Integer oldValue = lastVarbitValues.get(varbitId);
            if (oldValue != null && oldValue == newValue) return; // No actual change

            change.put("type", "varbit");
            change.put("id", varbitId);
            change.put("old", oldValue == null ? -1 : oldValue);
            lastVarbitValues.put(varbitId, newValue);
        }

        variableChanges.add(change);
        log.info("{} {} changed: {} -> {} (tick {})", change.get("type").toString().toUpperCase(), change.get("id"), change.get("old"), change.get("new"), change.get("tick"));
    }

    @Subscribe
    public void onVarClientIntChanged(VarClientIntChanged event) {
        if (!config.varbitChangeLogger()) return;

        int index = event.getIndex();
        int newValue = client.getVarcIntValue(index); // Fetch the new (current) value
        Integer oldValue = lastVarClientIntValues.getOrDefault(index, -1); // Use tracked old value
        if (oldValue == newValue) return; // No actual change (unlikely, but safe)

        Map<String, Object> change = new HashMap<>();
        change.put("type", "varclientint");
        change.put("id", index);
        change.put("old", oldValue);
        change.put("new", newValue);
        change.put("tick", client.getTickCount());

        variableChanges.add(change);
        log.info("VARCLIENTINT {} changed: {} -> {} (tick {})", index, oldValue, newValue, client.getTickCount());

        lastVarClientIntValues.put(index, newValue); // Update tracking for next change
    }

    public List<Map<String, Object>> getVariableChanges() {
        List<Map<String, Object>> copy = new ArrayList<>(variableChanges);
        variableChanges.clear();
        return copy;
    }

    @Subscribe
    public void onGameTick(GameTick event) {
        tickCount++; // Increment tick counter

        if (!client.isMenuOpen()) {
            currentMenuEntries = null;
        }

        if (config.locationEnabled()) {
            extractLocation();
        } else {
            playerLocationText = null;
        }

        if (config.questStatesEnabled()) {
            extractQuestStates();
        }

        if (config.skillLevelsEnabled()) {
            extractSkillLevels();
        }

        if (config.equippedGearEnabled()) {
            extractEquippedGear();
        }

        if (config.weightEnabled()) {
            extractWeight();
        } else {
            weightText = null;
        }

        if (config.runEnergyEnabled()) {
            extractRunEnergy();
        } else {
            runEnergyText = null;
        }

        if (config.healthEnabled()) {
            extractHealth();
        } else {
            healthText = null;
        }

        if (config.chatMessagesEnabled()) {
            extractChatMessages();
        }

        if (config.enableUnderAttackIndicator()) {
            updateUnderAttackStatus();
        } else {
            underAttack = false;
        }

        if (config.enableReachableIndicator() && underAttack) {
            reachableUnderAttack = false;
            Player localPlayer = client.getLocalPlayer();
            WorldPoint playerPos = localPlayer.getWorldLocation();
            LocalPoint destLocal = client.getLocalDestinationLocation();
            WorldPoint dest = destLocal != null ? WorldPoint.fromLocal(client, destLocal) : playerPos;
            int playerSpeed = (client.getEnergy() > 0 && client.getVarbitValue(173) == 1) ? 2 : 1;
            CollisionData[] collisionMaps = client.getCollisionMaps();
            int plane = client.getPlane();
            CollisionData collisionData = collisionMaps != null ? collisionMaps[plane] : null;
            if (collisionData == null) {
                return;
            }

            int[][] tempCollisionFlags = copyCollisionFlags(collisionData);

            for (NPC otherNpc : client.getNpcs()) {
                if (otherNpc != null && otherNpc.isDead()) continue;
                NPCComposition otherComp = otherNpc.getComposition();
                int otherSize = (otherComp != null) ? otherComp.getSize() : 1;
                WorldPoint otherPos = otherNpc.getWorldLocation();
                int ox = otherPos.getX() - client.getBaseX();
                int oy = otherPos.getY() - client.getBaseY();
                for (int dx = 0; dx < otherSize; dx++) {
                    for (int dy = 0; dy < otherSize; dy++) {
                        if (ox + dx >= 0 && oy + dy >= 0 && ox + dx < tempCollisionFlags.length && oy + dy < tempCollisionFlags[0].length) {
                            tempCollisionFlags[ox + dx][oy + dy] |= BLOCK_MOVEMENT_FULL;
                        }
                    }
                }
            }

            WorldPoint predictedPlayerPos = predictNextPosition(playerPos, dest, playerSpeed, 1, 1, tempCollisionFlags);

            for (NPC npc : client.getNpcs()) {
                if (npc != null && npc.getInteracting() == localPlayer) {
                    String name = npc.getName();
                    if (name != null) {
                        String lowerName = name.toLowerCase();
                        int cooldownTicks = cooldownByName.getOrDefault(lowerName, 4); // Default to 4 if not set
                        int lastAttack = npcLastAttackTicks.getOrDefault(npc.getIndex(), -100);
                        if (tickCount - lastAttack < cooldownTicks) {
                            continue;
                        }

                        WorldPoint npcPos = npc.getWorldLocation();
                        NPCComposition comp = npc.getComposition();
                        int size = (comp != null) ? comp.getSize() : 1;
                        WorldArea npcArea = npc.getWorldArea();
                        boolean currentlyInRange = npcArea.isInMeleeDistance(localPlayer.getWorldArea());

                        WorldPoint predictedNpcPos;
                        if (currentlyInRange) {
                            predictedNpcPos = npcPos;
                        } else {
                            predictedNpcPos = predictNextPosition(npcPos, playerPos, 1, size, size, tempCollisionFlags);
                        }

                        WorldArea predictedNpcArea = new WorldArea(predictedNpcPos.getX(), predictedNpcPos.getY(), size, size, predictedNpcPos.getPlane());
                        WorldArea predictedPlayerArea = new WorldArea(predictedPlayerPos, 1, 1);

                        if (predictedNpcArea.isInMeleeDistance(predictedPlayerArea)) {
                            reachableUnderAttack = true;
                            break;
                        }
                    }
                }
            }
        } else {
            reachableUnderAttack = false;
        }

        updateReferencePosition();
    }

    private int[][] copyCollisionFlags(CollisionData collisionData) {
        int[][] flags = collisionData.getFlags();
        int[][] copy = new int[flags.length][];
        for (int i = 0; i < flags.length; i++) {
            copy[i] = flags[i].clone();
        }
        return copy;
    }

    private void updateUnderAttackStatus() {
        Player local = client.getLocalPlayer();
        underAttack = false;

        for (NPC npc : client.getNpcs()) {
            if (npc != null && npc.getInteracting() == local) {
                underAttack = true;
                break;
            }
        }

        if (!underAttack) {
            for (Player player : client.getPlayers()) {
                if (player != null && player != local && player.getInteracting() == local) {
                    underAttack = true;
                    break;
                }
            }
        }
    }

    public boolean isUnderAttack() {
        return underAttack;
    }

    public boolean isReachableUnderAttack() {
        return reachableUnderAttack;
    }

    private WorldPoint predictNextPosition(WorldPoint start, WorldPoint target, int speed, int width, int height, int[][] tempCollisionFlags) {
        if (start.equals(target)) {
            return start;
        }
        List<WorldPoint> path = calculatePath(start, target, width, height, tempCollisionFlags);
        if (path.isEmpty() || path.size() == 1) {
            return start;
        }
        int steps = Math.min(speed, path.size() - 1);
        return path.get(steps);
    }

    private List<WorldPoint> calculatePath(WorldPoint start, WorldPoint target, int width, int height, int[][] tempCollisionFlags) {
        int plane = client.getPlane();
        int baseX = client.getBaseX();
        int baseY = client.getBaseY();

        int startX = start.getX() - baseX;
        int startY = start.getY() - baseY;
        int targetX = target.getX() - baseX;
        int targetY = target.getY() - baseY;

        Map<Point, Point> parent = new HashMap<>();
        Set<Point> visited = new HashSet<>();
        Queue<Point> queue = new ArrayDeque<>();
        Point startPoint = new Point(startX, startY);
        queue.add(startPoint);
        visited.add(startPoint);

        while (!queue.isEmpty() && visited.size() < 100) {
            Point current = queue.poll();
            if (current.x == targetX && current.y == targetY) {
                List<WorldPoint> path = new ArrayList<>();
                Point p = current;
                while (p != null) {
                    path.add(new WorldPoint(p.x + baseX, p.y + baseY, plane));
                    p = parent.get(p);
                }
                Collections.reverse(path);
                return path;
            }

            for (int d = 0; d < 4; d++) {
                int nx = current.x + DX[d];
                int ny = current.y + DY[d];
                Point next = new Point(nx, ny);
                if (nx < 0 || ny < 0 || nx + width - 1 >= tempCollisionFlags.length || ny + height - 1 >= tempCollisionFlags[0].length || visited.contains(next)) {
                    continue;
                }

                if (canMoveInDirection(current.x, current.y, d, width, height, tempCollisionFlags) && isAreaFree(nx, ny, width, height, tempCollisionFlags)) {
                    queue.add(next);
                    visited.add(next);
                    parent.put(next, current);
                }
            }
        }
        return Collections.emptyList();
    }

    private boolean isAreaFree(int x, int y, int width, int height, int[][] tempCollisionFlags) {
        for (int dx = 0; dx < width; dx++) {
            for (int dy = 0; dy < height; dy++) {
                int flags = tempCollisionFlags[x + dx][y + dy];
                if ((flags & BLOCK_MOVEMENT_FULL) != 0) {
                    return false;
                }
            }
        }
        return true;
    }

    private boolean canMoveInDirection(int x, int y, int dir, int width, int height, int[][] tempCollisionFlags) {
        int dx = DX[dir];
        int dy = DY[dir];
        int fromFlag = getCollisionFlagForDirection(dx, dy);
        int toFlag = getOppositeCollisionFlagForDirection(dx, dy);

        if (dx != 0) {
            int startX = (dx > 0) ? x + width - 1 : x;
            int newX = startX + dx;
            for (int py = y; py < y + height; py++) {
                int fromFlags = tempCollisionFlags[startX][py];
                int toFlags = tempCollisionFlags[newX][py];
                boolean blocked = (toFlags & (BLOCK_MOVEMENT_OBJECT | BLOCK_MOVEMENT_FLOOR | BLOCK_MOVEMENT_FULL)) != 0;

                if (!blocked) {
                    blocked = (fromFlags & fromFlag) != 0 || (toFlags & toFlag) != 0;
                }

                if (blocked) {
                    return false;
                }
            }
        } else if (dy != 0) {
            int startY = (dy > 0) ? y + height - 1 : y;
            int newY = startY + dy;
            for (int px = x; px < x + width; px++) {
                int fromFlags = tempCollisionFlags[px][startY];
                int toFlags = tempCollisionFlags[px][newY];
                boolean blocked = (toFlags & (BLOCK_MOVEMENT_OBJECT | BLOCK_MOVEMENT_FLOOR | BLOCK_MOVEMENT_FULL)) != 0;

                if (!blocked) {
                    blocked = (fromFlags & fromFlag) != 0 || (toFlags & toFlag) != 0;
                }

                if (blocked) {
                    return false;
                }
            }
        }
        return true;
    }

    private int getOppositeCollisionFlagForDirection(int dx, int dy) {
        if (dx == -1 && dy == 0) {
            return BLOCK_MOVEMENT_EAST;
        } else if (dx == 1 && dy == 0) {
            return BLOCK_MOVEMENT_WEST;
        } else if (dx == 0 && dy == -1) {
            return BLOCK_MOVEMENT_NORTH;
        } else if (dx == 0 && dy == 1) {
            return BLOCK_MOVEMENT_SOUTH;
        } else {
            return 0;
        }
    }

    private int getCollisionFlagForDirection(int dx, int dy) {
        if (dx == -1 && dy == 0) {
            return BLOCK_MOVEMENT_WEST;
        } else if (dx == 1 && dy == 0) {
            return BLOCK_MOVEMENT_EAST;
        } else if (dx == 0 && dy == -1) {
            return BLOCK_MOVEMENT_SOUTH;
        } else if (dx == 0 && dy == 1) {
            return BLOCK_MOVEMENT_NORTH;
        } else {
            return 0;
        }
    }

    private void updateReferencePosition() {
        Player player = client.getLocalPlayer();
        if (player != null) {
            WorldPoint currentPlayerPosition = player.getWorldLocation();
            if (referencePosition == null || !referencePosition.equals(currentPlayerPosition)) {
                referencePosition = currentPlayerPosition;
            }
        }
    }

    public WorldPoint getReferencePosition() {
        return referencePosition;
    }

    private void extractLocation() {
        WorldPoint location = client.getLocalPlayer().getWorldLocation();
        if (location != null) {
            int plane = location.getPlane();
            playerLocationText = String.format("Location: %d, %d, Plane %d", location.getX(), location.getY(), plane);
            log.info(playerLocationText);
            System.out.println(playerLocationText);
        } else {
            log.warn("Failed to get player location.");
        }
    }

    private void extractQuestStates() {
        StringBuilder sb = new StringBuilder();
        for (Quest quest : Quest.values()) {
            QuestState state = quest.getState(client);
            sb.append(String.format("Quest: %s - State: %s%n", quest.getName(), state));
        }
        String questStates = sb.toString();
        log.info(questStates);
        System.out.println(questStates);
    }

    private void extractSkillLevels() {
        StringBuilder sb = new StringBuilder();
        for (Skill skill : Skill.values()) {
            int level = client.getRealSkillLevel(skill);
            int xp = client.getSkillExperience(skill);
            sb.append(String.format("Skill: %s - Level: %d - XP: %d%n", skill.getName(), level, xp));
        }
        skillLevelsText = sb.toString();
        log.info(skillLevelsText);
    }

    private void extractWeight() {
        int weight = client.getWeight();
        weightText = String.format("Weight: %d kg", weight);
        log.info(weightText);
        System.out.println(weightText);
    }

    private void extractRunEnergy() {
        int energy = client.getEnergy();
        runEnergyText = String.format("Run Energy: %d%%", energy / 100);
        log.info(runEnergyText);
        System.out.println(runEnergyText);
    }

    private void extractHealth() {
        int currentHp = client.getBoostedSkillLevel(Skill.HITPOINTS);
        int maxHp = client.getRealSkillLevel(Skill.HITPOINTS);
        int currentPrayer = client.getBoostedSkillLevel(Skill.PRAYER);
        int maxPrayer = client.getRealSkillLevel(Skill.PRAYER);
        healthText = String.format("HP: %d/%d, Prayer: %d/%d", currentHp, maxHp, currentPrayer, maxPrayer);
        log.info(healthText);
        System.out.println(healthText);
    }

    private void extractChatMessages() {
        final Widget chatbox = client.getWidget(WidgetInfo.CHATBOX_MESSAGE_LINES);
        if (chatbox != null) {
            StringBuilder sb = new StringBuilder();
            for (Widget widget : chatbox.getChildren()) {
                if (widget == null) continue;
                String message = widget.getText();
                if (message != null && !message.isEmpty()) {
                    sb.append(message).append("\n");
                }
            }
            chatMessagesText = sb.toString();
            log.info(chatMessagesText);
        } else {
            log.warn("Chatbox widget is null.");
        }
    }

    private void extractEquippedGear() {
        ItemContainer equipment = client.getItemContainer(InventoryID.EQUIPMENT);
        if (equipment != null) {
            int totalAstab = 0, totalAslash = 0, totalAcrush = 0, totalAmagic = 0, totalArange = 0;
            int totalDstab = 0, totalDslash = 0, totalDcrush = 0, totalDmagic = 0, totalDrange = 0;
            int totalStr = 0, totalMdmg = 0, totalRstr = 0, totalPrayer = 0;

            for (Item item : equipment.getItems()) {
                if (item.getId() != -1) {
                    String itemName = itemManager.getItemComposition(item.getId()).getName();
                    log.info("Equipped item: {}", itemName);

                    ItemStats stats = itemManager.getItemStats(item.getId(), false);
                    if (stats != null && stats.getEquipment() != null) {
                        ItemEquipmentStats equipStats = stats.getEquipment();

                        log.info("Bonuses for {}: Astab={}, Aslash={}, Acrush={}, Amagic={}, Arange={}, " +
                                        "Dstab={}, Dslash={}, Dcrush={}, Dmagic={}, Drange={}, " +
                                        "Str={}, Mdmg={}, Rstr={}, Prayer={}",
                                itemName,
                                equipStats.getAstab(), equipStats.getAslash(), equipStats.getAcrush(),
                                equipStats.getAmagic(), equipStats.getArange(),
                                equipStats.getDstab(), equipStats.getDslash(), equipStats.getDcrush(),
                                equipStats.getDmagic(), equipStats.getDrange(),
                                equipStats.getStr(), equipStats.getMdmg(), equipStats.getRstr(), equipStats.getPrayer());

                        totalAstab += equipStats.getAstab();
                        totalAslash += equipStats.getAslash();
                        totalAcrush += equipStats.getAcrush();
                        totalAmagic += equipStats.getAmagic();
                        totalArange += equipStats.getArange();
                        totalDstab += equipStats.getDstab();
                        totalDslash += equipStats.getDslash();
                        totalDcrush += equipStats.getDcrush();
                        totalDmagic += equipStats.getDmagic();
                        totalDrange += equipStats.getDrange();
                        totalStr += equipStats.getStr();
                        totalMdmg += equipStats.getMdmg();
                        totalRstr += equipStats.getRstr();
                        totalPrayer += equipStats.getPrayer();
                    }
                }
            }

            equippedGearText = String.format(
                    "Total Bonuses: Astab=%d, Aslash=%d, Acrush=%d, Amagic=%d, Arange=%d, " +
                            "Dstab=%d, Dslash=%d, Dcrush=%d, Dmagic=%d, Drange=%d, " +
                            "Str=%d, Mdmg=%d, Rstr=%d, Prayer=%d",
                    totalAstab, totalAslash, totalAcrush, totalAmagic, totalArange,
                    totalDstab, totalDslash, totalDcrush, totalDmagic, totalDrange,
                    totalStr, totalMdmg, totalRstr, totalPrayer
            );
            log.info(equippedGearText);
            System.out.println(equippedGearText);
        } else {
            equippedGearText = "No equipment found.";
            log.warn(equippedGearText);
        }
    }

    public Map<String, Object> getAggressiveNpcs(Map<String, Object> params) {
        String npcName = params != null ? (String) params.get("name") : null;
        boolean found = false;
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> aggressiveNpcs = new ArrayList<>();

        Player localPlayer = client.getLocalPlayer();
        WorldPoint playerPos = localPlayer.getWorldLocation();
        LocalPoint destLocal = client.getLocalDestinationLocation();
        WorldPoint dest = destLocal != null ? WorldPoint.fromLocal(client, destLocal) : playerPos;
        int playerSpeed = (client.getEnergy() > 0 && client.getVarbitValue(173) == 1) ? 2 : 1;
        CollisionData[] collisionMaps = client.getCollisionMaps();
        int plane = client.getPlane();
        CollisionData collisionData = collisionMaps != null ? collisionMaps[plane] : null;
        int[][] tempCollisionFlags = null;
        if (collisionData != null) {
            tempCollisionFlags = copyCollisionFlags(collisionData);
            for (NPC otherNpc : client.getNpcs()) {
                if (otherNpc != null && otherNpc.isDead()) continue;
                NPCComposition otherComp = otherNpc.getComposition();
                int otherSize = (otherComp != null) ? otherComp.getSize() : 1;
                WorldPoint otherPos = otherNpc.getWorldLocation();
                int ox = otherPos.getX() - client.getBaseX();
                int oy = otherPos.getY() - client.getBaseY();
                for (int dx = 0; dx < otherSize; dx++) {
                    for (int dy = 0; dy < otherSize; dy++) {
                        if (ox + dx >= 0 && oy + dy >= 0 && ox + dx < tempCollisionFlags.length && oy + dy < tempCollisionFlags[0].length) {
                            tempCollisionFlags[ox + dx][oy + dy] |= BLOCK_MOVEMENT_FULL;
                        }
                    }
                }
            }
        }

        WorldPoint predictedPlayerPos = playerPos;
        if (tempCollisionFlags != null) {
            predictedPlayerPos = predictNextPosition(playerPos, dest, playerSpeed, 1, 1, tempCollisionFlags);
        }

        for (NPC npc : client.getNpcs()) {
            if (npc != null && npc.getInteracting() == client.getLocalPlayer()) {
                String name = npc.getName();
                String lowerName = (name != null) ? name.toLowerCase() : "";
                int cooldownTicks = cooldownByName.getOrDefault(lowerName, 4); // Default to 4 if not set
                int lastAttack = npcLastAttackTicks.getOrDefault(npc.getIndex(), -100);
                int ticksSince = tickCount - lastAttack;
                boolean onCooldown = ticksSince < cooldownTicks;
                int cooldownRemaining = onCooldown ? (cooldownTicks - ticksSince) : 0;

                boolean canReach = false;
                if (tempCollisionFlags != null) {
                    WorldPoint npcPos = npc.getWorldLocation();
                    NPCComposition comp = npc.getComposition();
                    int size = (comp != null) ? comp.getSize() : 1;
                    WorldArea npcArea = npc.getWorldArea();
                    boolean currentlyInRange = npcArea.isInMeleeDistance(localPlayer.getWorldArea());

                    WorldPoint predictedNpcPos;
                    if (currentlyInRange) {
                        predictedNpcPos = npcPos;
                    } else {
                        predictedNpcPos = predictNextPosition(npcPos, playerPos, 1, size, size, tempCollisionFlags);
                    }

                    WorldArea predictedNpcArea = new WorldArea(predictedNpcPos.getX(), predictedNpcPos.getY(), size, size, predictedNpcPos.getPlane());
                    WorldArea predictedPlayerArea = new WorldArea(predictedPlayerPos, 1, 1);
                    canReach = predictedNpcArea.isInMeleeDistance(predictedPlayerArea);
                }

                Map<String, Object> npcData = new HashMap<>();
                npcData.put("name", name);
                npcData.put("id", npc.getId());
                npcData.put("health", npc.getHealthRatio());
                npcData.put("location", npc.getWorldLocation().toString());
                npcData.put("onCooldown", onCooldown);
                npcData.put("cooldownRemaining", cooldownRemaining);
                npcData.put("attackSpeed", cooldownTicks);
                npcData.put("canReach", canReach);
                aggressiveNpcs.add(npcData);

                if (canReach) {
                    log.info("Reachable {} ID: {}, Tile: {}", name, npc.getId(), npc.getWorldLocation().toString());
                }

                if (npcName != null && name != null && name.equalsIgnoreCase(npcName)) {
                    found = true;
                    result.put("aggressive", true);
                    result.put("name", name);
                    result.put("id", npc.getId());
                    result.put("health", npc.getHealthRatio());
                    result.put("location", npc.getWorldLocation().toString());
                    result.put("onCooldown", onCooldown);
                    result.put("cooldownRemaining", cooldownRemaining);
                    result.put("attackSpeed", cooldownTicks);
                    result.put("canReach", canReach);
                    return result;
                }
            }
        }

        if (npcName != null) {
            result.put("aggressive", found);
            if (found) {
                Map<String, Object> firstMatch = aggressiveNpcs.get(0);
                result.putAll(firstMatch);
                result.put("aggressive", true);
            }
            return result;
        } else {
            result.put("aggressiveNpcs", aggressiveNpcs);
            return result;
        }
    }

    public void setNpcConfig(Map<String, Object> params) {
        @SuppressWarnings("unchecked")
        Map<String, Object> npcDataMap = (Map<String, Object>) params.get("npc_data");
        for (Map.Entry<String, Object> entry : npcDataMap.entrySet()) {
            String name = entry.getKey();
            @SuppressWarnings("unchecked")
            Map<String, Object> info = (Map<String, Object>) entry.getValue();
            List<Integer> anims = new ArrayList<>();
            @SuppressWarnings("unchecked")
            List<Object> animList = (List<Object>) info.get("attack_anims");
            for (Object o : animList) {
                anims.add(((Number) o).intValue());
            }
            Integer cooldown = ((Number) info.get("cooldown")).intValue();
            String lowerName = name.toLowerCase();
            attackAnimsByName.put(lowerName, anims);
            cooldownByName.put(lowerName, cooldown);
            log.info("Set NPC config: {} (normalized to {}) with animations {} and cooldown {} ticks", name, lowerName, anims, cooldown);
        }
    }

    private class AsdUnderAttackOverlay extends Overlay {
        private final AsdPlugin plugin;
        private final AsdConfig config;

        @Inject
        private AsdUnderAttackOverlay(AsdPlugin plugin, AsdConfig config) {
            this.plugin = plugin;
            this.config = config;
            setPosition(OverlayPosition.TOP_RIGHT);
            setPriority(OverlayPriority.LOW);
        }

        @Override
        public Dimension render(Graphics2D graphics) {
            if (!config.enableUnderAttackIndicator()) {
                return null;
            }

            graphics.setColor(plugin.isUnderAttack() ? config.underAttackColor() : config.notUnderAttackColor());
            graphics.fillRect(0, 0, 20, 20);
            return new Dimension(20, 20);
        }
    }

    private class AsdReachableAttackOverlay extends Overlay {
        private final AsdPlugin plugin;
        private final AsdConfig config;

        @Inject
        private AsdReachableAttackOverlay(AsdPlugin plugin, AsdConfig config) {
            this.plugin = plugin;
            this.config = config;
            setPosition(OverlayPosition.TOP_RIGHT);
            setPriority(OverlayPriority.LOW);
        }

        @Override
        public Dimension render(Graphics2D graphics) {
            if (!config.enableReachableIndicator()) {
                return null;
            }

            graphics.setColor(plugin.isReachableUnderAttack() ? config.underAttackColor() : config.notUnderAttackColor());
            graphics.fillRect(0, 20, 20, 20);
            return new Dimension(20, 20);
        }
    }
}