package net.runelite.client.plugins.asd;

import net.runelite.api.widgets.Widget;
import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.client.ui.overlay.*;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Point;
import java.util.ArrayList;
import java.util.List;
import java.awt.Rectangle;
import java.awt.geom.Rectangle2D;
import javax.inject.Inject;
import java.awt.*;
import java.awt.geom.Area;
import java.util.Set;
import java.util.*;
import java.util.stream.Collectors;

import net.runelite.api.Client;
import net.runelite.api.Scene;
import net.runelite.api.Perspective;
import net.runelite.api.GroundObject;
import net.runelite.api.WallObject;
import net.runelite.api.DecorativeObject;
import net.runelite.api.GameObject;
import net.runelite.api.TileObject;
import net.runelite.api.CollisionDataFlag;
import net.runelite.api.CollisionData;
import net.runelite.api.NPC;
import net.runelite.api.NPCComposition;
import java.awt.Polygon;
import java.awt.FontMetrics;
import java.net.Socket;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.BufferedWriter;
import java.io.IOException;
import com.google.gson.Gson;

@Slf4j
public class MainOverlay extends Overlay {
    private final Client client;
    private final AsdConfig config;
    private final AsdPlugin plugin;

    private static final int BLOCK_MOVEMENT_NORTH = CollisionDataFlag.BLOCK_MOVEMENT_NORTH;
    private static final int BLOCK_MOVEMENT_EAST = CollisionDataFlag.BLOCK_MOVEMENT_EAST;
    private static final int BLOCK_MOVEMENT_SOUTH = CollisionDataFlag.BLOCK_MOVEMENT_SOUTH;
    private static final int BLOCK_MOVEMENT_WEST = CollisionDataFlag.BLOCK_MOVEMENT_WEST;
    private static final int BLOCK_MOVEMENT_FULL = CollisionDataFlag.BLOCK_MOVEMENT_FULL;

    @Inject
    public MainOverlay(Client client, AsdConfig config, AsdPlugin plugin) {
        this.client = client;
        this.config = config;
        this.plugin = plugin;

        setPosition(OverlayPosition.DYNAMIC);
        setLayer(OverlayLayer.ABOVE_WIDGETS);
    }

    @Override
    public Dimension render(Graphics2D graphics) {
        int padding = 5;
        int lineHeight = 15;
        graphics.setFont(new Font("Arial", Font.PLAIN, config.overlayTextSize()));
        graphics.setColor(config.overlayTextColor());

        List<String> overlayTexts = new ArrayList<>();

        if (plugin.playerLocationText != null) {
            overlayTexts.add(plugin.playerLocationText);
        }

        if (plugin.weightText != null) {
            overlayTexts.add(plugin.weightText);
        }

        if (plugin.runEnergyText != null) {
            overlayTexts.add(plugin.runEnergyText);
        }

        if (plugin.healthText != null) {
            overlayTexts.add(plugin.healthText);
        }

        if (config.playerAnimationEnabled()) {
            int playerAnimation = client.getLocalPlayer().getAnimation();
            String playerAnimationText = playerAnimation != -1 ?
                    String.format("Player Animation: %d", playerAnimation) : "Player Animation: None";
            overlayTexts.add(playerAnimationText);
        }

        if (config.showClientCamera()) {
            int cameraPitch = client.getCameraPitch();
            int cameraYaw = client.getCameraYaw();
            int clientZoom = client.getScale();
            String cameraInfo = String.format("Camera Pitch: %d, Yaw: %d, Zoom: %d", cameraPitch, cameraYaw, clientZoom);
            overlayTexts.add(cameraInfo);
        }

        if (config.showClientTick()) {
            int clientTick = client.getTickCount();
            String clientTickText = String.format("Client Tick: %d", clientTick);
            overlayTexts.add(clientTickText);
        }

        if (!overlayTexts.isEmpty()) {
            FontMetrics metrics = graphics.getFontMetrics();
            int overlayWidth = 0;
            for (String text : overlayTexts) {
                int textWidth = metrics.stringWidth(text);
                if (textWidth > overlayWidth) {
                    overlayWidth = textWidth;
                }
            }
            overlayWidth += padding * 2;
            int overlayHeight = overlayTexts.size() * lineHeight + padding * 2;

            int xPosition = 5;
            int yPosition = client.getCanvasHeight() - overlayHeight - 165;

            graphics.setColor(config.overlayBackgroundColor());
            graphics.fillRect(xPosition, yPosition, overlayWidth, overlayHeight);
            graphics.setColor(config.overlayBorderColor());
            graphics.drawRect(xPosition, yPosition, overlayWidth, overlayHeight);

            Color shadowColor = config.overlayTextShadowColor();
            int shadowOffset = 1;

            int textYPosition = yPosition + padding + metrics.getAscent();
            for (String text : overlayTexts) {
                int textXPosition = xPosition + padding;

                graphics.setColor(shadowColor);
                graphics.drawString(text, textXPosition + shadowOffset, textYPosition + shadowOffset);
                graphics.drawString(text, textXPosition - shadowOffset, textYPosition + shadowOffset);
                graphics.drawString(text, textXPosition + shadowOffset, textYPosition - shadowOffset);
                graphics.drawString(text, textXPosition - shadowOffset, textYPosition - shadowOffset);

                graphics.setColor(config.overlayTextColor());
                graphics.drawString(text, textXPosition, textYPosition);

                textYPosition += lineHeight;
            }
        }

        drawInventoryItemIDs(graphics);

        Shape originalClip = graphics.getClip();
        Shape gameClip = getGameViewportClip();
        graphics.setClip(gameClip);

        if (config.drawAllTileCoordinates()) {
            drawTileCoordinates(graphics, false);
        } else if (config.drawWalkableTileCoordinates()) {
            drawTileCoordinates(graphics, true);
        }

        if (config.extractLocalObjectsEnabled()) {
            drawLocalObjects(graphics);
        }
        highlightGameObjects(graphics);
        graphics.setClip(originalClip);

        if (config.enableMouseHoverInteractOptions()) {
            drawInteractOptions(graphics);
        }

        return null;
    }

    private Shape getGameViewportClip() {
        int canvasWidth = client.getCanvasWidth();
        int canvasHeight = client.getCanvasHeight();

        Rectangle chatboxBounds = new Rectangle(0, canvasHeight - 165, canvasWidth, 165);
        Rectangle minimapBounds = new Rectangle(canvasWidth - 249, 0, 249, canvasHeight);

        Area gameViewport = new Area(new Rectangle(0, 0, canvasWidth, canvasHeight));
        gameViewport.subtract(new Area(chatboxBounds));
        gameViewport.subtract(new Area(minimapBounds));

        return gameViewport;
    }

    private enum Direction {
        NORTH(0, 1),
        SOUTH(0, -1),
        EAST(1, 0),
        WEST(-1, 0),
        NORTHEAST(1, 1),
        NORTHWEST(-1, 1),
        SOUTHEAST(1, -1),
        SOUTHWEST(-1, -1);

        private final int dx;
        private final int dy;

        Direction(int dx, int dy) {
            this.dx = dx;
            this.dy = dy;
        }

        public int getDx() {
            return dx;
        }

        public int getDy() {
            return dy;
        }
    }

    private Set<WorldPoint> getReachableTiles(WorldPoint startPosition, int radius) {
        Set<WorldPoint> reachableTiles = new HashSet<>();
        Queue<WorldPoint> queue = new LinkedList<>();
        Set<WorldPoint> visited = new HashSet<>();

        queue.add(startPosition);
        visited.add(startPosition);

        while (!queue.isEmpty()) {
            WorldPoint current = queue.poll();
            reachableTiles.add(current);

            if (current.distanceTo(startPosition) >= radius) {
                continue;
            }

            for (Direction direction : Direction.values()) {
                int dx = direction.getDx();
                int dy = direction.getDy();

                WorldPoint neighbor = current.dx(dx).dy(dy);

                if (visited.contains(neighbor)) {
                    continue;
                }

                if (canMoveTo(current, neighbor)) {
                    queue.add(neighbor);
                    visited.add(neighbor);
                }
            }
        }

        return reachableTiles;
    }

    private Set<WorldPoint> getAllTilesWithinRadius(WorldPoint center, int radius) {
        Set<WorldPoint> tiles = new HashSet<>();

        int plane = center.getPlane();

        for (int dx = -radius; dx <= radius; dx++) {
            for (int dy = -radius; dy <= radius; dy++) {
                int x = center.getX() + dx;
                int y = center.getY() + dy;

                WorldPoint tile = new WorldPoint(x, y, plane);
                tiles.add(tile);
            }
        }

        return tiles;
    }

    private void drawInteractOptions(Graphics2D graphics) {
        Point mousePosition = client.getMouseCanvasPosition();
        int mouseX = mousePosition.getX();
        int mouseY = mousePosition.getY();

        MenuEntry[] menuEntries = client.getMenuEntries();
        if (menuEntries == null || menuEntries.length == 0) {
            return;
        }

        graphics.setFont(new Font("Arial", Font.PLAIN, config.interactOptionFontSize()));
        graphics.setColor(config.interactOptionColor());
        FontMetrics fontMetrics = graphics.getFontMetrics();

        double regularOptionHeight = 14.5;
        double walkHereOptionHeight = 18;
        double previousOptionHeight = 0;

        int menuWidth = 0;
        for (MenuEntry entry : menuEntries) {
            String optionText = entry.getOption() + " " + entry.getTarget();
            int textWidth = fontMetrics.stringWidth(optionText);
            if (textWidth > menuWidth) {
                menuWidth = textWidth;
            }
        }

        double yPosition = mouseY + 23;

        double totalMenuHeight = 0;

        List<Double> optionPositions = new ArrayList<>();

        List<Map<String, Object>> interactOptionsWithMiddlePoints = new ArrayList<>();

        for (int i = menuEntries.length - 1; i >= 0; i--) {
            MenuEntry entry = menuEntries[i];
            String option = entry.getOption();
            String target = entry.getTarget();
            String optionText = option + " " + target;

            double currentOptionHeight = option.equals("Walk here") ? walkHereOptionHeight : regularOptionHeight;

            if (i != menuEntries.length - 1) {
                yPosition += (previousOptionHeight / 2.0) + (currentOptionHeight / 2.0);
            }

            int textBaselineY = (int) Math.round(yPosition + fontMetrics.getAscent() / 2);

            graphics.setColor(Color.BLACK);
            graphics.drawString(optionText, mouseX + 1, textBaselineY + 1);

            graphics.setColor(config.interactOptionColor());
            graphics.drawString(optionText, mouseX, textBaselineY);

            log.info("Option '{}': x={}, y={}", optionText, mouseX, textBaselineY);

            Map<String, Object> optionData = new HashMap<>();
            optionData.put("option", option);
            optionData.put("target", target);
            optionData.put("middle_point", new Point(mouseX, textBaselineY));
            interactOptionsWithMiddlePoints.add(optionData);

            previousOptionHeight = currentOptionHeight;

            totalMenuHeight += currentOptionHeight;
            optionPositions.add(yPosition);
        }

        sendInteractOptionsToSocket(interactOptionsWithMiddlePoints);

        graphics.setColor(new Color(0, 0, 0, 128));
        int bgTopY = (int) Math.round(optionPositions.get(0) - (previousOptionHeight / 2));
        graphics.fillRect(mouseX - 5, bgTopY, menuWidth + 10, (int) Math.round(totalMenuHeight));
    }

    private void sendInteractOptionsToSocket(List<Map<String, Object>> interactOptionsWithMiddlePoints) {
        Gson gson = new Gson();
        String jsonOptions = gson.toJson(interactOptionsWithMiddlePoints);

        try (Socket socket = new Socket("localhost", 9999);
             OutputStream outputStream = socket.getOutputStream();
             BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(outputStream))) {

            writer.write(jsonOptions);
            writer.flush();
        } catch (IOException e) {
            log.error("Error sending interact options to socket: ", e);
        }
    }

    private void drawTileCoordinates(Graphics2D graphics, boolean useReachability) {
        WorldPoint referencePosition = plugin.getReferencePosition();
        if (referencePosition == null) {
            return;
        }

        int radius = config.tileRadius();
        Set<WorldPoint> tilesToDraw;

        if (useReachability) {
            tilesToDraw = getReachableTiles(referencePosition, radius);
        } else {
            tilesToDraw = getAllTilesWithinRadius(referencePosition, radius);
        }

        Font originalFont = graphics.getFont();
        int padding = 2;
        int minFontSize = 2;

        for (WorldPoint worldPoint : tilesToDraw) {
            LocalPoint tilePoint = LocalPoint.fromWorld(client, worldPoint);
            if (tilePoint == null) {
                continue;
            }

            Polygon tilePolygon = Perspective.getCanvasTilePoly(client, tilePoint);
            if (tilePolygon == null) {
                continue;
            }

            graphics.setColor(config.tileOutlineColor());
            graphics.draw(tilePolygon);

            String textX = "x: " + worldPoint.getX();
            String textY = "y: " + worldPoint.getY();

            String textScreenX = null;
            String textScreenY = null;

            if (config.showClientCoordinates()) {
                Point tileScreenPoint = Perspective.localToCanvas(client, tilePoint, client.getPlane(), 0);
                if (tileScreenPoint != null) {
                    textScreenX = "sx: " + tileScreenPoint.getX();
                    textScreenY = "sy: " + tileScreenPoint.getY();
                } else {
                    textScreenX = "sx: N/A";
                    textScreenY = "sy: N/A";
                }
            }

            List<String> lines = new ArrayList<>();
            lines.add(textX);
            lines.add(textY);
            if (config.showClientCoordinates()) {
                lines.add(textScreenX);
                lines.add(textScreenY);
            }

            int fontSize = config.tileTextSize();
            graphics.setFont(new Font("Arial", Font.PLAIN, fontSize));
            FontMetrics fontMetrics = graphics.getFontMetrics();

            int textHeight = fontMetrics.getHeight();
            int totalTextHeight = textHeight * lines.size();

            Rectangle tileBounds = tilePolygon.getBounds();
            float heightScale = (float) (tileBounds.height - padding * 2) / totalTextHeight;
            float scaleFactor = Math.min(heightScale, 1.0f);

            int newFontSize = Math.max((int) (fontSize * scaleFactor), minFontSize);
            graphics.setFont(new Font("Arial", Font.PLAIN, newFontSize));
            fontMetrics = graphics.getFontMetrics();
            textHeight = fontMetrics.getHeight();

            int textYPos = tileBounds.y + (tileBounds.height - totalTextHeight) / 2 + fontMetrics.getAscent();

            for (String line : lines) {
                int textWidth = fontMetrics.stringWidth(line);
                int textXPos = tileBounds.x + (tileBounds.width - textWidth) / 2;

                graphics.setColor(Color.BLACK);
                graphics.drawString(line, textXPos + 1, textYPos + 1);

                graphics.setColor(config.tileTextColor());
                graphics.drawString(line, textXPos, textYPos);

                textYPos += textHeight;
            }

            graphics.setFont(originalFont);
        }
    }

    private boolean canMoveTo(WorldPoint from, WorldPoint to) {
        int dx = to.getX() - from.getX();
        int dy = to.getY() - from.getY();

        if (Math.abs(dx) == 1 && Math.abs(dy) == 1) {
            WorldPoint stepX = from.dx(dx);
            WorldPoint stepY = from.dy(dy);

            return canMoveToCardinal(from, stepX) && canMoveToCardinal(from, stepY) && canMoveToCardinal(from, to);
        } else if ((Math.abs(dx) == 1 && dy == 0) || (dx == 0 && Math.abs(dy) == 1)) {
            return canMoveToCardinal(from, to);
        } else {
            return false;
        }
    }

    private boolean canMoveToCardinal(WorldPoint from, WorldPoint to) {
        int dx = to.getX() - from.getX();
        int dy = to.getY() - from.getY();
        int plane = from.getPlane();

        CollisionData[] collisionMaps = client.getCollisionMaps();
        if (collisionMaps == null || plane >= collisionMaps.length) {
            return false;
        }
        CollisionData collisionData = collisionMaps[plane];

        int x = from.getX() - client.getBaseX();
        int y = from.getY() - client.getBaseY();

        int[][] flags = collisionData.getFlags();
        if (flags == null || x < 0 || y < 0 || x >= flags.length || y >= flags[x].length) {
            return false;
        }

        int collisionFlags = flags[x][y];

        int directionFlag = getCollisionFlagForDirection(dx, dy);
        if (directionFlag == 0) {
            return false;
        }

        if ((collisionFlags & directionFlag) != 0) {
            return false;
        }

        int destX = to.getX() - client.getBaseX();
        int destY = to.getY() - client.getBaseY();
        if (destX < 0 || destY < 0 || destX >= flags.length || destY >= flags[destX].length) {
            return false;
        }

        int destCollisionFlags = flags[destX][destY];

        if ((destCollisionFlags & BLOCK_MOVEMENT_FULL) != 0) {
            return false;
        }

        return true;
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

    private void drawInventoryItemIDs(Graphics2D graphics) {
        if (!config.inventoryItemIDsEnabled() && !config.displayItemIDOverlays()) {
            return;
        }

        Widget inventoryWidget = client.getWidget(WidgetInfo.INVENTORY);
        if (inventoryWidget == null || inventoryWidget.isHidden()) {
            return;
        }

        Widget[] items = inventoryWidget.getDynamicChildren();
        if (items == null) {
            return;
        }

        if (config.displayItemIDOverlays()) {
            graphics.setFont(new Font("Arial", Font.PLAIN, config.inventoryItemTextSize()));
        }
        FontMetrics fontMetrics = graphics.getFontMetrics();

        for (Widget itemWidget : items) {
            int itemId = itemWidget.getItemId();
            if (itemId <= 0 || itemId == 6512) {
                continue;
            }

            Point itemCanvasLocation = itemWidget.getCanvasLocation();
            if (itemCanvasLocation == null) {
                continue;
            }

            int x = itemCanvasLocation.getX();
            int y = itemCanvasLocation.getY();

            int width = itemWidget.getWidth();
            int height = itemWidget.getHeight();

            if (width <= 0 || height <= 0) {
                continue;
            }

            int centerX = x + width / 2;
            int centerY = y + height / 2;

            ItemComposition itemComposition = client.getItemDefinition(itemId);
            String itemName = itemComposition != null ? itemComposition.getName() : "Unknown";

            if (config.inventoryItemIDsEnabled()) {
                System.out.printf("Item ID: %d, Item Name: %s, x, y = %d, %d%n", itemId, itemName, centerX, centerY);
            }

            if (config.displayItemIDOverlays()) {
                String text = String.valueOf(itemId);
                int textWidth = fontMetrics.stringWidth(text);
                int textHeight = fontMetrics.getAscent();

                int textX = centerX - textWidth / 2;
                int textY = centerY + textHeight / 2 - fontMetrics.getDescent();

                graphics.setColor(Color.BLACK);
                graphics.drawString(text, textX + 1, textY + 1);

                graphics.setColor(config.inventoryItemTextColor());
                graphics.drawString(text, textX, textY);
            }
        }
    }

    private void highlightGameObjects(Graphics2D graphics) {
        if (!config.gameObjectHighlightEnabled()) {
            return;
        }

        Scene scene = client.getScene();
        Tile[][] tiles = scene.getTiles()[client.getPlane()];

        String filterInput = config.gameObjectFilter().toLowerCase();
        String[] filters = filterInput.isEmpty() ? new String[0] : filterInput.split(",");
        Set<String> filterSet = Arrays.stream(filters)
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toSet());

        for (Tile[] tileRow : tiles) {
            for (Tile tile : tileRow) {
                if (tile == null) continue;

                for (GameObject gameObject : tile.getGameObjects()) {
                    if (gameObject == null) continue;

                    ObjectComposition objectComp = client.getObjectDefinition(gameObject.getId());
                    if (objectComp == null || objectComp.getName() == null) continue;

                    String objectName = objectComp.getName().toLowerCase();
                    int objectId = gameObject.getId();

                    boolean matchesFilter = filterSet.isEmpty() || filterSet.stream().anyMatch(filter ->
                            objectName.contains(filter) || filter.equals(String.valueOf(objectId))
                    );

                    if (matchesFilter) {
                        Shape objectHull = gameObject.getConvexHull();
                        if (objectHull != null) {
                            graphics.setColor(config.gameObjectOutlineColor());
                            graphics.draw(objectHull);

                            String text = String.format("%s (ID: %d)", objectComp.getName(), objectId);

                            Rectangle bounds = objectHull.getBounds();
                            int centerX = (int) bounds.getCenterX();
                            int centerY = (int) bounds.getCenterY();

                            graphics.setFont(new Font("Arial", Font.PLAIN, config.gameObjectTextSize()));
                            graphics.setColor(config.gameObjectTextColor());
                            FontMetrics fm = graphics.getFontMetrics();
                            int textWidth = fm.stringWidth(text);
                            int textHeight = fm.getHeight();

                            int textX = centerX - textWidth / 2;
                            int textY = centerY + textHeight / 2 - fm.getDescent();

                            graphics.setColor(Color.BLACK);
                            graphics.drawString(text, textX + 1, textY + 1);

                            graphics.setColor(config.gameObjectTextColor());
                            graphics.drawString(text, textX, textY);
                        }
                    }
                }
            }
        }
    }

    private void drawLocalObjects(Graphics2D graphics) {
        Scene scene = client.getScene();
        int plane = client.getPlane();

        Tile[][] tiles = scene.getTiles()[plane];

        graphics.setFont(new Font("Arial", Font.PLAIN, config.objectIdTextSize()));
        Font originalFont = graphics.getFont();
        int minFontSize = 9;

        String[] userActions = config.interactableActions().split(",");
        Set<String> actionSet = Arrays.stream(userActions)
                .map(String::trim)
                .collect(Collectors.toSet());

        for (Tile[] tileRow : tiles) {
            for (Tile tile : tileRow) {
                if (tile == null) {
                    continue;
                }

                processGameObjects(graphics, tile.getGameObjects(), actionSet, originalFont, minFontSize);

                WallObject wallObject = tile.getWallObject();
                if (wallObject != null && wallObject.getId() != -1) {
                    processTileObject(graphics, wallObject, actionSet, originalFont, minFontSize);
                }

                DecorativeObject decoObject = tile.getDecorativeObject();
                if (decoObject != null && decoObject.getId() != -1) {
                    processTileObject(graphics, decoObject, actionSet, originalFont, minFontSize);
                }

                GroundObject groundObject = tile.getGroundObject();
                if (groundObject != null && groundObject.getId() != -1) {
                    processTileObject(graphics, groundObject, actionSet, originalFont, minFontSize);
                }
            }
        }
    }

    private void processGameObjects(Graphics2D graphics, GameObject[] gameObjects, Set<String> actionSet, Font originalFont, int minFontSize) {
        for (GameObject gameObject : gameObjects) {
            if (gameObject == null || gameObject.getId() == -1) {
                continue;
            }
            processTileObject(graphics, gameObject, actionSet, originalFont, minFontSize);
        }
    }

    private void processTileObject(Graphics2D graphics, TileObject tileObject, Set<String> actionSet, Font originalFont, int minFontSize) {
        int id = tileObject.getId();

        ObjectComposition objectComposition = client.getObjectDefinition(id);
        if (objectComposition == null) {
            return;
        }

        String[] actions = objectComposition.getActions();

        boolean hasInteractableAction = false;
        for (String action : actions) {
            if (action != null && actionSet.contains(action)) {
                hasInteractableAction = true;
                break;
            }
        }

        String objectName = objectComposition.getName();
        if (objectName != null && (
                objectName.equalsIgnoreCase("Door") ||
                        objectName.equalsIgnoreCase("Gate") ||
                        objectName.equalsIgnoreCase("Drawer") ||
                        objectName.equalsIgnoreCase("Drawers"))
        ) {
            hasInteractableAction = true;
        }

        if (!hasInteractableAction) {
            return;
        }

        Shape objectHull = null;
        if (tileObject instanceof GameObject) {
            objectHull = ((GameObject) tileObject).getConvexHull();
        } else if (tileObject instanceof WallObject) {
            objectHull = ((WallObject) tileObject).getConvexHull();
        } else if (tileObject instanceof DecorativeObject) {
            objectHull = ((DecorativeObject) tileObject).getConvexHull();
        } else if (tileObject instanceof GroundObject) {
            objectHull = ((GroundObject) tileObject).getConvexHull();
        }

        if (objectHull != null) {
            graphics.setColor(config.objectOutlineColor());
            graphics.draw(objectHull);
        }

        String text = String.valueOf(id);

        Rectangle2D objectBounds = objectHull != null ? objectHull.getBounds2D() : null;
        if (objectBounds == null) {
            return;
        }

        int padding = 2;

        String fontName = config.objectIdFont();
        int fontSize = config.objectIdTextSize();
        graphics.setFont(new Font(fontName, Font.PLAIN, fontSize));
        FontMetrics fontMetrics = graphics.getFontMetrics();
        int textWidth = fontMetrics.stringWidth(text);
        int textHeight = fontMetrics.getHeight();

        float scaleFactor = 1.0f;
        int objectWidth = (int) objectBounds.getWidth();
        int objectHeight = (int) objectBounds.getHeight();

        if (objectWidth > 0 && objectHeight > 0) {
            float widthScale = (float) (objectWidth - padding * 2) / textWidth;
            float heightScale = (float) (objectHeight - padding * 2) / textHeight;
            scaleFactor = Math.min(widthScale, heightScale);
            scaleFactor = Math.min(scaleFactor, 1.0f);
            int newFontSize = Math.max((int) (fontSize * scaleFactor), minFontSize);
            graphics.setFont(new Font(fontName, Font.PLAIN, newFontSize));
            fontMetrics = graphics.getFontMetrics();
            textWidth = fontMetrics.stringWidth(text);
            textHeight = fontMetrics.getHeight();
        }

        int textX = (int) (objectBounds.getCenterX() - textWidth / 2);
        int textY = (int) (objectBounds.getCenterY() + fontMetrics.getAscent() / 2) - textHeight / 2;

        graphics.setColor(Color.BLACK);
        graphics.drawString(text, textX + 1, textY + 1);

        graphics.setColor(config.objectIdTextColor());
        graphics.drawString(text, textX, textY);

        graphics.setFont(originalFont);
    }
    public List<Map<String, Object>> findLocalObjects(Map<String, Object> params) {
        List<Map<String, Object>> objectList = new ArrayList<>();
        try {
            String idParam = (String) params.get("id");
            String targetAction = (String) params.get("action");
            boolean searchById = isNumeric(idParam);
            int targetId = searchById ? Integer.parseInt(idParam) : -1;
            String targetName = searchById ? null : idParam.toLowerCase();
            boolean specificTile = params.containsKey("tile") && params.get("tile") instanceof Map;
            WorldPoint searchCenter;
            int searchRadius;
            if (specificTile) {
                @SuppressWarnings("unchecked")
                Map<String, Object> tileParam = (Map<String, Object>) params.get("tile");
                int tx = ((Number) tileParam.get("x")).intValue();
                int ty = ((Number) tileParam.get("y")).intValue();
                searchCenter = new WorldPoint(tx, ty, client.getPlane());
                searchRadius = 0;
            } else {
                searchCenter = client.getLocalPlayer().getWorldLocation();
                searchRadius = ((Number) params.getOrDefault("radius", 20)).intValue();
            }
            Set<WorldPoint> searchTiles = getAllTilesWithinRadius(searchCenter, searchRadius);
            Scene scene = client.getScene();
            int plane = client.getPlane();
            int baseX = client.getBaseX();
            int baseY = client.getBaseY();
            for (WorldPoint wp : searchTiles) {
                int sx = wp.getX() - baseX;
                int sy = wp.getY() - baseY;
                if (sx < 0 || sx >= 104 || sy < 0 || sy >= 104) {
                    continue;
                }
                Tile tile = scene.getTiles()[plane][sx][sy];
                if (tile == null) {
                    continue;
                }
                processGameObjectsForCollection(tile.getGameObjects(), targetId, targetName, targetAction, wp, objectList, "game_object", searchById);
                WallObject wo = tile.getWallObject();
                if (wo != null && matchesObject(wo.getId(), targetId, client.getObjectDefinition(wo.getId()).getName(), targetName, searchById)) {
                    ObjectComposition comp = client.getObjectDefinition(wo.getId());
                    if (compHasAction(comp, targetAction)) {
                        Shape hull = wo.getConvexHull();
                        Map<String, Object> data = createObjectData(wo.getId(), comp, "wall_object", wp, hull);
                        objectList.add(data);
                    }
                }
                DecorativeObject deco = tile.getDecorativeObject();
                if (deco != null && matchesObject(deco.getId(), targetId, client.getObjectDefinition(deco.getId()).getName(), targetName, searchById)) {
                    ObjectComposition comp = client.getObjectDefinition(deco.getId());
                    if (compHasAction(comp, targetAction)) {
                        Shape hull = deco.getConvexHull();
                        Map<String, Object> data = createObjectData(deco.getId(), comp, "decorative_object", wp, hull);
                        objectList.add(data);
                    }
                }
                GroundObject ground = tile.getGroundObject();
                if (ground != null && matchesObject(ground.getId(), targetId, client.getObjectDefinition(ground.getId()).getName(), targetName, searchById)) {
                    ObjectComposition comp = client.getObjectDefinition(ground.getId());
                    if (compHasAction(comp, targetAction)) {
                        Shape hull = ground.getConvexHull();
                        Map<String, Object> data = createObjectData(ground.getId(), comp, "ground_object", wp, hull);
                        objectList.add(data);
                    }
                }
            }
        } catch (Exception e) {
            log.error("Error handling local_object request: ", e);
        }
        return objectList;
    }

    private boolean isNumeric(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }
        try {
            Integer.parseInt(str);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    private boolean matchesObject(int objId, int targetId, String objName, String targetName, boolean searchById) {
        if (searchById) {
            return objId == targetId;
        } else {
            return objName != null && objName.toLowerCase().equals(targetName);
        }
    }

    private void processGameObjectsForCollection(GameObject[] gameObjects, int targetId, String targetName, String targetAction, WorldPoint tilePos, List<Map<String, Object>> objects, String type, boolean searchById) {
        for (GameObject gameObject : gameObjects) {
            if (gameObject == null) {
                continue;
            }
            if (matchesObject(gameObject.getId(), targetId, client.getObjectDefinition(gameObject.getId()).getName(), targetName, searchById)) {
                ObjectComposition comp = client.getObjectDefinition(gameObject.getId());
                if (compHasAction(comp, targetAction)) {
                    Shape hull = gameObject.getConvexHull();
                    Map<String, Object> data = createObjectData(gameObject.getId(), comp, type, tilePos, hull);
                    objects.add(data);
                }
            }
        }
    }

    private boolean compHasAction(ObjectComposition comp, String action) {
        if (comp == null) {
            return false;
        }
        String[] acts = comp.getActions();
        if (acts == null) {
            return false;
        }
        for (String a : acts) {
            if (a != null && a.equalsIgnoreCase(action)) {
                return true;
            }
        }
        return false;
    }

    private Map<String, Object> createObjectData(int id, ObjectComposition comp, String type, WorldPoint wp, Shape hull) {
        Map<String, Object> data = new HashMap<>();
        data.put("id", id);
        data.put("name", comp.getName());
        data.put("type", type);
        data.put("tile", Map.of("x", wp.getX(), "y", wp.getY(), "plane", wp.getPlane()));
        if (hull != null) {
            Rectangle2D b = hull.getBounds2D();
            data.put("on_screen", true);
            data.put("middle_point", Map.of("x", (int) b.getCenterX(), "y", (int) b.getCenterY()));
        } else {
            LocalPoint lp = LocalPoint.fromWorld(client, wp);
            Point sp = (lp != null) ? Perspective.localToCanvas(client, lp, wp.getPlane(), 0) : null;
            if (sp != null) {
                data.put("on_screen", false);
                data.put("middle_point", Map.of("x", sp.getX(), "y", sp.getY()));
            } else {
                data.put("on_screen", false);
                data.put("middle_point", null);
            }
        }
        return data;
    }
}