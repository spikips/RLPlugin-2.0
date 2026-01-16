package net.runelite.client.plugins.asd;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.events.GameTick;
import net.runelite.api.events.MenuOptionClicked;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.api.widgets.WidgetType;
import net.runelite.client.callback.ClientThread;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.input.MouseListener;
import net.runelite.client.input.MouseManager;
import net.runelite.client.util.Text;

import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.event.MouseEvent;
import java.awt.Polygon;
import java.time.Instant;
import java.util.*;
import java.util.Deque;
import java.util.stream.Collectors;

import static net.runelite.api.Perspective.COSINE;
import static net.runelite.api.Perspective.LOCAL_TILE_SIZE;
import static net.runelite.api.Perspective.SINE;
import static net.runelite.api.Perspective.getCanvasTilePoly;

@Slf4j
@Singleton
public class ClickHandler implements RequestHandler, MouseListener {
    @Inject
    private Client client;

    @Inject
    private MouseManager mouseManager;

    @Inject
    private ClientThread clientThread;

    @Inject
    private AsdConfig config;

    @Inject
    private SocketServer socketServer;  // NEW: For broadcasting clicks
    private List<Map<String, Object>> lastWidgetChanges;

    private final Deque<Map<String, Object>> recentClicks = new ArrayDeque<>();
    private static final int MAX_CLICKS_STORED = 10;

    // General widget change tracking
    private final Map<String, WidgetState> previousWidgetStates = new HashMap<>();
    private boolean snapshotTaken = false;

    private static class WidgetState {
        int spriteId = -1;
        String text = null;

        WidgetState(int spriteId, String text) {
            this.spriteId = spriteId;
            this.text = text;
        }
    }

    private boolean isChatboxRelated(Widget widget) {
        Widget parent = widget;
        while (parent != null) {
            if (parent.getId() == WidgetInfo.CHATBOX_MESSAGES.getId()) {
                return true;
            }
            parent = parent.getParent();
        }
        return false;
    }

    public void register() {
        mouseManager.registerMouseListener(this);
    }

    public void unregister() {
        mouseManager.unregisterMouseListener(this);
    }

    @Override
    public Object handle(String function, Map<String, Object> params) {
        if (!config.enableClickLogging()) {
            return new ResponseData().setError("Click logging disabled in config");
        }

        if ("last_click".equals(function)) {
            return recentClicks.isEmpty() ? null : recentClicks.peekLast();
        } else if ("recent_clicks".equals(function)) {
            int limit = params.containsKey("limit") ? ((Number) params.get("limit")).intValue() : 5;
            return recentClicks.stream().skip(Math.max(0, recentClicks.size() - limit)).collect(Collectors.toList());
        }
        return new ResponseData().setError("Unknown click function: " + function);
    }

    // Updated onMenuOptionClicked with fallback widget detection and dialogue option handling
    @Subscribe
    public void onMenuOptionClicked(MenuOptionClicked event) {
        if (!config.enableClickLogging()) return;

        Map<String, Object> clickData = new HashMap<>();
        clickData.put("tick", client.getTickCount());
        clickData.put("type", "menu_option");
        clickData.put("option", event.getMenuOption());
        clickData.put("target", Text.removeTags(event.getMenuTarget()));

        MenuAction action = event.getMenuAction();

        Point mousePos = client.getMouseCanvasPosition();
        clickData.put("canvas_pos", Map.of("x", mousePos.getX(), "y", mousePos.getY()));

        boolean onMinimap = isOnMinimap(mousePos.getX(), mousePos.getY());
        if (onMinimap) {
            clickData.put("is_minimap_click", true);
            WorldPoint minimapTile = minimapPointToWorld(mousePos);
            if (minimapTile != null) {
                clickData.put("minimap_tile", Map.of("x", minimapTile.getX(), "y", minimapTile.getY(), "plane", minimapTile.getPlane()));
            }
        }

        // Capture widget info if available
        Widget clickedWidget = event.getWidget();
        if (clickedWidget == null) {
            clickedWidget = findWidgetAt(mousePos);
        }
        if (clickedWidget != null) {
            Map<String, Object> widgetData = new HashMap<>();
            widgetData.put("id", clickedWidget.getId());
            widgetData.put("type", clickedWidget.getType());
            if (clickedWidget.getText() != null && !clickedWidget.getText().isEmpty()) {
                widgetData.put("text", clickedWidget.getText());
            }
            if (clickedWidget.getName() != null && !clickedWidget.getName().isEmpty()) {
                widgetData.put("name", clickedWidget.getName());
            }
            Rectangle bounds = clickedWidget.getBounds();
            if (bounds != null) {
                widgetData.put("bounds", Map.of(
                        "x", bounds.x,
                        "y", bounds.y,
                        "width", bounds.width,
                        "height", bounds.height
                ));
            }
            clickData.put("widget", widgetData);
            clickData.put("entity_type", "widget");  // Override to indicate widget interaction

            // Special handling for dialogue "Continue" to set option to widget text
            if ("Continue".equals(event.getMenuOption()) && clickedWidget.getText() != null && !clickedWidget.getText().isEmpty()) {
                clickData.put("option", clickedWidget.getText());
            }
        }

        // Take snapshot on any menu click that could change widgets
        if (action != MenuAction.WALK) {  // Exclude pure walk to reduce noise
            log.info("Taking widget snapshot after menu click: {} {}", event.getMenuOption(), event.getMenuTarget());
            snapshotWidgets();
        }

        if (action == MenuAction.WALK) {
            Map<String, Integer> tile = unpackTile(event.getParam0(), event.getParam1());
            clickData.put("clicked_tile", tile);
        } else if (action.toString().startsWith("NPC_")) {
            clickData.put("entity_type", "npc");
            clickData.put("npc_name", Text.removeTags(event.getMenuTarget()));
            int npcIndex = event.getParam1();
            clickData.put("npc_index", npcIndex);
            net.runelite.api.NPC npc = findNpcByIndex(npcIndex);
            if (npc != null) {
                clickData.put("npc_id", npc.getId());
            } else {
                clickData.put("npc_id", event.getId());
            }
        } else if (action.toString().startsWith("GAME_OBJECT_")) {
            clickData.put("entity_type", "object");
            clickData.put("object_id", event.getId());
            clickData.put("object_name", Text.removeTags(event.getMenuTarget()));
            clickData.put("object_tile", unpackTile(event.getParam0(), event.getParam1()));
        }

        addToRecentClicks(clickData);
        log.info("Menu click: {}", clickData);
    }

    private Widget findWidgetAt(Point canvasPoint) {
        int x = canvasPoint.getX();
        int y = canvasPoint.getY();

        for (Widget root : client.getWidgetRoots()) {
            if (root == null || root.isHidden()) continue;

            Widget found = findWidgetRecursive(root, x, y);
            if (found != null) {
                return found;
            }
        }
        return null;
    }

    private Widget findWidgetRecursive(Widget widget, int x, int y) {
        if (widget == null || widget.isHidden()) return null;

        Rectangle bounds = widget.getBounds();
        if (bounds != null && bounds.contains(x, y)) {
            // Check children first for more specific widget
            Widget[] children = widget.getDynamicChildren();
            if (children != null) {
                for (Widget child : children) {
                    Widget found = findWidgetRecursive(child, x, y);
                    if (found != null) return found;
                }
            }

            children = widget.getStaticChildren();
            if (children != null) {
                for (Widget child : children) {
                    Widget found = findWidgetRecursive(child, x, y);
                    if (found != null) return found;
                }
            }

            children = widget.getNestedChildren();
            if (children != null) {
                for (Widget child : children) {
                    Widget found = findWidgetRecursive(child, x, y);
                    if (found != null) return found;
                }
            }

            // If no child contains, return this widget
            return widget;
        }

        return null;
    }

    // onGameTick – unchanged from previous fix (just call the new detector)
    @Subscribe
    public void onGameTick(GameTick event) {
        if (snapshotTaken) {
            log.info("Checking for widget changes on tick {}", client.getTickCount());
            lastWidgetChanges = detectWidgetChanges();

            if (!lastWidgetChanges.isEmpty() && !recentClicks.isEmpty()) {
                Map<String, Object> lastClick = recentClicks.peekLast();
                lastClick.put("widget_changes", lastWidgetChanges);
                log.info("{} widget change(s) associated with last click", lastWidgetChanges.size());
            } else if (lastWidgetChanges.isEmpty()) {
                log.info("No widget changes detected on this tick");
            }
            snapshotTaken = false;
        }
    }

    @Override
    public MouseEvent mousePressed(MouseEvent event) {
        if (!config.enableClickLogging() || event.getButton() != 1) return event;

        Map<String, Object> clickData = new HashMap<>();
        clickData.put("tick", client.getTickCount());
        clickData.put("type", "left_click");

        double clickX = event.getPoint().getX();
        double clickY = event.getPoint().getY();
        Point rlPos = new Point((int) clickX, (int) clickY);
        clickData.put("canvas_pos", Map.of("x", (int) clickX, "y", (int) clickY));

        log.info("Taking widget snapshot after left click at ({}, {})", (int) clickX, (int) clickY);
        snapshotWidgets();

        final Map<String, Object>[] detectionHolder = new Map[1];
        clientThread.invoke(() -> {
            detectionHolder[0] = detectLeftClick(clickX, clickY, rlPos);
        });
        Map<String, Object> detection = detectionHolder[0];
        if (detection != null) {
            clickData.putAll(detection);
        }

        addToRecentClicks(clickData);
        log.info("Left click: {}", clickData);
        return event;
    }

    @Override public MouseEvent mouseReleased(MouseEvent event) { return event; }
    @Override public MouseEvent mouseClicked(MouseEvent event) { return event; }
    @Override public MouseEvent mouseEntered(MouseEvent event) { return event; }
    @Override public MouseEvent mouseExited(MouseEvent event) { return event; }
    @Override public MouseEvent mouseDragged(MouseEvent event) { return event; }
    @Override public MouseEvent mouseMoved(MouseEvent event) { return event; }

    private void addToRecentClicks(Map<String, Object> clickData) {
        synchronized (recentClicks) {
            recentClicks.addLast(clickData);
            if (recentClicks.size() > MAX_CLICKS_STORED) {
                recentClicks.removeFirst();
            }
        }
    }

    private void snapshotWidgets() {
        previousWidgetStates.clear();

        for (Widget root : client.getWidgetRoots()) {
            if (root == null) continue;
            snapshotWidgetRecursive(root, "");
        }

        log.info("Widget snapshot taken: {} widgets stored", previousWidgetStates.size());
        snapshotTaken = true;
    }

    private int snapshotWidgetRecursive(Widget widget, String path) {
        if (widget == null || widget.isHidden()) return 0;

        String key = widget.getId() + path;

        int spriteId = widget.getSpriteId();
        String currentText = null;
        if (widget.getType() == WidgetType.TEXT) {
            String t = widget.getText();
            if (t != null && !t.isEmpty()) {
                currentText = t;
            }
        }

        boolean store = spriteId > -1 || (currentText != null && isChatboxRelated(widget));

        if (store) {
            previousWidgetStates.put(key, new WidgetState(spriteId, currentText));
            return 1;
        }

        int count = 0;
        Widget[] children = widget.getDynamicChildren();
        if (children != null) {
            for (int i = 0; i < children.length; i++) {
                count += snapshotWidgetRecursive(children[i], path + "_" + i);
            }
        }

        children = widget.getStaticChildren();
        if (children != null) {
            for (int i = 0; i < children.length; i++) {
                count += snapshotWidgetRecursive(children[i], path + "_" + i);
            }
        }

        children = widget.getNestedChildren();
        if (children != null) {
            for (int i = 0; i < children.length; i++) {
                count += snapshotWidgetRecursive(children[i], path + "_" + i);
            }
        }

        return count;
    }

    private List<Map<String, Object>> detectWidgetChanges() {
        List<Map<String, Object>> changes = new ArrayList<>();

        for (Widget root : client.getWidgetRoots()) {
            if (root == null || root.isHidden()) continue;

            checkWidgetRecursive(root, "", changes);
        }

        if (changes.isEmpty()) {
            log.info("No widget changes detected on this tick");
        } else {
            log.info("{} widget changes detected on this tick", changes.size());
        }

        return changes;
    }

    private void checkWidgetRecursive(Widget widget, String path, List<Map<String, Object>> changes) {
        if (widget == null || widget.isHidden()) return;

        String key = widget.getId() + path;

        WidgetState previous = previousWidgetStates.get(key);

        int currentSpriteId = widget.getSpriteId();
        String currentText = null;
        if (widget.getType() == WidgetType.TEXT) {
            String t = widget.getText();
            if (t != null && !t.isEmpty()) {
                currentText = t;
            }
        }

        boolean isChat = isChatboxRelated(widget);

        boolean spriteChanged = previous != null && currentSpriteId != previous.spriteId;
        boolean textChanged = previous != null && !Objects.equals(currentText, previous.text);

        boolean isNew = previous == null;
        boolean hasNewSprite = isNew && currentSpriteId > -1;
        boolean hasNewText = isNew && currentText != null && isChat;

        boolean hasSpriteChange = spriteChanged || hasNewSprite;
        boolean hasTextChange = textChanged || hasNewText;

        boolean isClickable = widget.getOnOpListener() != null;

        boolean addChange = (hasSpriteChange && isClickable) || hasTextChange;

        if (addChange) {
            Map<String, Object> change = new HashMap<>();
            change.put("widget_id", widget.getId());
            change.put("path", path);
            change.put("type", isNew ? "new" : "changed");

            if (hasSpriteChange) {
                change.put("old_sprite", previous != null ? previous.spriteId : -1);
                change.put("new_sprite", currentSpriteId);
            }

            if (hasTextChange) {
                change.put("old_text", previous != null ? previous.text : null);
                change.put("new_text", currentText);
            }

            changes.add(change);

            log.info("Widget change detected: ID={}, Path={}, Type={}, Old Sprite={}, New Sprite={}, Old Text={}, New Text={}",
                    widget.getId(), path, change.get("type"),
                    change.getOrDefault("old_sprite", "N/A"),
                    change.getOrDefault("new_sprite", "N/A"),
                    change.getOrDefault("old_text", "N/A"),
                    change.getOrDefault("new_text", "N/A"));
        }

        Widget[] children = widget.getDynamicChildren();
        if (children != null) {
            for (int i = 0; i < children.length; i++) {
                checkWidgetRecursive(children[i], path + "_" + i, changes);
            }
        }

        children = widget.getStaticChildren();
        if (children != null) {
            for (int i = 0; i < children.length; i++) {
                checkWidgetRecursive(children[i], path + "_" + i, changes);
            }
        }

        children = widget.getNestedChildren();
        if (children != null) {
            for (int i = 0; i < children.length; i++) {
                checkWidgetRecursive(children[i], path + "_" + i, changes);
            }
        }
    }

    private Map<String, Integer> unpackTile(int param0, int param1) {
        int sceneX = param0 & 0x3FFF;
        int sceneY = param0 >> 14 & 0x3FFF;
        LocalPoint local = LocalPoint.fromScene(sceneX, sceneY);
        WorldPoint world = WorldPoint.fromLocal(client, local);
        Map<String, Integer> tile = new HashMap<>();
        tile.put("x", world.getX());
        tile.put("y", world.getY());
        tile.put("plane", world.getPlane());
        return tile;
    }

    private boolean isOnMinimap(int x, int y) {
        Widget minimapWidget = getMinimapWidget();
        if (minimapWidget == null) return false;
        Rectangle bounds = minimapWidget.getBounds();
        return bounds != null && bounds.contains(x, y);
    }

    private WorldPoint minimapPointToWorld(Point pos) {
        try {
            if (client.isInInstancedRegion()) return null;

            Widget minimapDrawWidget = getMinimapWidget();
            if (minimapDrawWidget == null) return null;

            int centerX = minimapDrawWidget.getCanvasLocation().getX() + minimapDrawWidget.getWidth() / 2;
            int centerY = minimapDrawWidget.getCanvasLocation().getY() + minimapDrawWidget.getHeight() / 2;

            double rx = pos.getX() - centerX;
            double ry = pos.getY() - centerY;

            int angle = client.getCameraYawTarget() & 0x7FF;
            double sin = SINE[angle] / 65536.0;
            double cos = COSINE[angle] / 65536.0;

            double rotatedX = cos * rx + sin * ry;
            double rotatedY = sin * rx - cos * ry;

            double pixelsPerTile = client.getMinimapZoom();
            double zoom = pixelsPerTile / LOCAL_TILE_SIZE;

            double dx = rotatedX / zoom;
            double dy = rotatedY / zoom;

            LocalPoint playerLocal = client.getLocalPlayer().getLocalLocation();
            LocalPoint hoverLocal = new LocalPoint((int)(playerLocal.getX() + dx), (int)(playerLocal.getY() + dy));

            return WorldPoint.fromLocal(client, hoverLocal);
        } catch (Exception e) {
            log.error("Error calculating minimap tile", e);
            return null;
        }
    }

    private Widget getMinimapWidget() {
        if (client.isResized()) {
            return client.getVarbitValue(Varbits.SIDE_PANELS) == 1
                    ? client.getWidget(WidgetInfo.RESIZABLE_MINIMAP_DRAW_AREA)
                    : client.getWidget(WidgetInfo.RESIZABLE_MINIMAP_STONES_DRAW_AREA);
        }
        return client.getWidget(WidgetInfo.FIXED_VIEWPORT_MINIMAP_DRAW_AREA);
    }

    private net.runelite.api.NPC findNpcByIndex(int index) {
        for (net.runelite.api.NPC npc : client.getNpcs()) {
            if (npc.getIndex() == index) {
                return npc;
            }
        }
        return null;
    }

    // Updated detectLeftClick to handle widget clicks if not scene
    private Map<String, Object> detectLeftClick(double clickX, double clickY, Point rlPos) {
        Map<String, Object> data = new HashMap<>();
        int plane = client.getPlane();
        boolean onMinimap = isOnMinimap(rlPos.getX(), rlPos.getY());

        if (onMinimap) {
            data.put("is_minimap_click", true);
            WorldPoint minimapTile = minimapPointToWorld(rlPos);
            if (minimapTile != null) {
                data.put("minimap_tile", Map.of("x", minimapTile.getX(), "y", minimapTile.getY(), "plane", minimapTile.getPlane()));
                return data;
            }
        }

        // NPCs
        for (net.runelite.api.NPC npc : client.getNpcs()) {
            Shape hull = npc.getConvexHull();
            if (hull != null && hull.contains(clickX, clickY)) {
                data.put("type", "npc");
                data.put("npc_id", npc.getId());
                data.put("npc_name", npc.getName() != null ? npc.getName() : "Unknown");
                WorldPoint wp = npc.getWorldLocation();
                data.put("npc_tile", Map.of("x", wp.getX(), "y", wp.getY(), "plane", wp.getPlane()));
                return data;
            }
        }

        // Objects
        for (int x = 0; x < Constants.SCENE_SIZE; x++) {
            for (int y = 0; y < Constants.SCENE_SIZE; y++) {
                net.runelite.api.Tile tile = client.getScene().getTiles()[plane][x][y];
                if (tile == null) continue;

                for (net.runelite.api.GameObject obj : tile.getGameObjects()) {
                    if (obj == null) continue;

                    Shape hull = obj.getConvexHull();
                    if (hull != null && hull.contains(clickX, clickY)) {
                        data.put("type", "object");
                        data.put("object_id", obj.getId());
                        data.put("object_name", client.getObjectDefinition(obj.getId()).getName());
                        WorldPoint wp = WorldPoint.fromScene(client, x, y, plane);
                        data.put("object_tile", Map.of("x", wp.getX(), "y", wp.getY(), "plane", wp.getPlane()));
                        return data;
                    }
                }
            }
        }

        // Fallback tile
        for (int x = 0; x < Constants.SCENE_SIZE; x++) {
            for (int y = 0; y < Constants.SCENE_SIZE; y++) {
                LocalPoint local = LocalPoint.fromScene(x, y);
                Polygon poly = getCanvasTilePoly(client, local);
                if (poly != null && poly.contains(clickX, clickY)) {
                    data.put("type", "tile");
                    WorldPoint wp = WorldPoint.fromScene(client, x, y, plane);
                    data.put("tile", Map.of("x", wp.getX(), "y", wp.getY(), "plane", wp.getPlane()));
                    return data;
                }
            }
        }

        // If not on scene, check for widget
        Widget clickedWidget = findWidgetAt(rlPos);
        if (clickedWidget != null) {
            data.put("type", "widget");
            data.put("widget_id", clickedWidget.getId());
            data.put("widget_type", clickedWidget.getType());
            if (clickedWidget.getText() != null && !clickedWidget.getText().isEmpty()) {
                data.put("widget_text", clickedWidget.getText());
            }
            if (clickedWidget.getName() != null && !clickedWidget.getName().isEmpty()) {
                data.put("widget_name", clickedWidget.getName());
            }
            Rectangle bounds = clickedWidget.getBounds();
            if (bounds != null) {
                data.put("widget_bounds", Map.of(
                        "x", bounds.x,
                        "y", bounds.y,
                        "width", bounds.width,
                        "height", bounds.height
                ));
            }
            return data;
        }

        return null;
    }
}