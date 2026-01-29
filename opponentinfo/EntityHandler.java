package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Point;
import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.client.game.ItemManager;
import net.runelite.client.plugins.opponentinfo.CustomOpponentInfoPlugin;

import javax.inject.Inject;
import java.awt.*;
import java.util.List;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
public class EntityHandler implements RequestHandler {
    @Inject
    private Client client;

    @Inject
    private ItemManager itemManager;

    @Inject
    private Gson gson;

    @Setter
    private CustomOpponentInfoPlugin customOpponentInfoPlugin;

    @Override
    public Object handle(String function, Map<String, Object> params) {
        switch (function) {
            case "npc":
                return handleNpcRequest(params);
            case "opponentInfo":
                return handleOpponentInfoRequest(params);
            case "pick":
                return handlePickRequest(params);
            default:
                return new ResponseData().setError("Unknown entity-related function: " + function);
        }
    }

    private Object handleNpcRequest(Map<String, Object> params) {
        String idFilter = (String) params.getOrDefault("id", "");
        String nameFilter = (String) params.getOrDefault("name", "");
        boolean includeTile = Boolean.TRUE.equals(params.get("tile"));
        boolean includeMiddlePoint = params.containsKey("middle_point");
        boolean includeAnimation = Boolean.TRUE.equals(params.get("animation"));
        boolean includeSize = Boolean.TRUE.equals(params.get("size"));
        Boolean inCombatFilter = (Boolean) params.get("in_combat");

        List<Map<String, Object>> npcList = new ArrayList<>();
        Random random = new Random();

        for (NPC npc : client.getNpcs()) {
            NPCComposition composition = npc.getComposition();
            if (composition == null || composition.getName() == null) continue;

            boolean matchesId = idFilter.isEmpty() || String.valueOf(npc.getId()).equals(idFilter);
            boolean matchesName = nameFilter.isEmpty() || composition.getName().toLowerCase().contains(nameFilter.toLowerCase());
            boolean isInCombat = npc.getInteracting() != null;
            boolean matchesCombatFilter = inCombatFilter == null
                    || (inCombatFilter && isInCombat)
                    || (!inCombatFilter && !isInCombat);

            if (matchesId && matchesName && matchesCombatFilter) {
                Map<String, Object> npcData = new HashMap<>();
                npcData.put("name", composition.getName());
                npcData.put("id", npc.getId());
                if (includeTile) {
                    WorldPoint location = getNpcNortheasternTile(npc);
                    npcData.put("tile", Map.of(
                            "x", location.getX(),
                            "y", location.getY(),
                            "plane", location.getPlane()
                    ));
                }
                if (includeMiddlePoint) {
                    Shape convexHull = npc.getConvexHull();
                    if (params.get("middle_point") == Boolean.FALSE) {
                        Map<String, Integer> randomPoint = getRandomPointInShape(convexHull, random);
                        if (randomPoint != null) {
                            npcData.put("middle_point", randomPoint);
                        }
                    } else {
                        LocalPoint lp = npc.getLocalLocation();
                        Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane(), npc.getLogicalHeight() / 2);
                        if (screenPoint != null) {
                            npcData.put("middle_point", Map.of(
                                    "x", screenPoint.getX(),
                                    "y", screenPoint.getY()
                            ));
                        }
                    }
                }
                if (includeAnimation) {
                    npcData.put("animation", npc.getAnimation());
                }
                if (includeSize) {
                    npcData.put("size", composition.getSize());
                }
                npcList.add(npcData);
            }
        }
        return npcList;
    }

    private WorldPoint getNpcNortheasternTile(NPC npc) {
        NPCComposition composition = npc.getComposition();
        if (composition == null) {
            return null;
        }
        WorldPoint npcWorldPoint = npc.getWorldLocation();
        int npcSize = composition.getSize();
        if (npcSize <= 1) {
            return npcWorldPoint;
        }
        return new WorldPoint(
                npcWorldPoint.getX() + (npcSize - 1),
                npcWorldPoint.getY() + (npcSize - 1),
                npcWorldPoint.getPlane()
        );
    }

    private Map<String, Integer> getRandomPointInShape(Shape shape, Random random) {
        if (shape == null) {
            log.warn("Shape is null, cannot generate random point");
            return null;
        }
        Rectangle bounds = shape.getBounds();
        int minX = bounds.x;
        int minY = bounds.y;
        int maxX = bounds.x + bounds.width;
        int maxY = bounds.y + bounds.height;

        for (int i = 0; i < 100; i++) {
            int x = minX + random.nextInt(maxX - minX + 1);
            int y = minY + random.nextInt(maxY - minY + 1);
            if (shape.contains(x, y)) {
                log.debug("Random point generated: x={}, y={}", x, y);
                return Map.of("x", x, "y", y);
            }
        }
        int centerX = bounds.x + bounds.width / 2;
        int centerY = bounds.y + bounds.height / 2;
        log.warn("No random point found after 100 attempts, using center: x={}, y={}", centerX, centerY);
        return Map.of("x", centerX, "y", centerY);
    }

    private Object handleOpponentInfoRequest(Map<String, Object> params) {
        NPC lastOpponent = (NPC) customOpponentInfoPlugin.getLastOpponent();
        Map<String, Object> response = new HashMap<>();
        if (lastOpponent != null) {
            int health = (int) Math.round(lastOpponent.getHealthRatio() / 4.0);
            int animation = lastOpponent.getAnimation();
            WorldPoint worldPoint = getNpcNortheasternTile(lastOpponent);
            int size = lastOpponent.getComposition().getSize();
            response.put("health", health);
            response.put("animation", animation);
            response.put("tile", Map.of("x", worldPoint.getX(), "y", worldPoint.getY()));
            response.put("size", size);
        } else {
            response.put("health", -1);
            response.put("animation", -1);
            response.put("tile", Map.of("x", -1, "y", -1));
            response.put("size", -1);
        }
        return response;
    }

    private Object handlePickRequest(Map<String, Object> params) {
        int x = ((Double) params.get("x")).intValue();
        int y = ((Double) params.get("y")).intValue();
        int size = ((Double) params.get("size")).intValue();
        String itemName = (String) params.get("item");

        List<Map<String, Object>> groundItemDataList = getGroundItemsInRange(x, y, size, itemName);

        if (groundItemDataList.isEmpty()) {
            log.info("No ground items found in the specified range.");
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("function", "pick");
            errorResponse.put("item", itemName);
            errorResponse.put("error", "Item not found");
            return errorResponse;
        } else {
            log.info("Found ground items: {}", groundItemDataList.size());
            Map<String, Object> response = new HashMap<>();
            response.put("function", "pick");
            response.put("item", itemName);
            response.put("items", groundItemDataList);
            return response;
        }
    }

    private List<Map<String, Object>> getGroundItemsInRange(int x, int y, int size, String itemName) {
        Scene scene = client.getScene();
        Tile[][][] tiles = scene.getTiles();
        List<Map<String, Object>> groundItemDataList = new ArrayList<>();

        int baseX = client.getBaseX();
        int baseY = client.getBaseY();
        int localStartX = x - baseX - size + 1;
        int localStartY = y - baseY - size + 1;
        int localEndX = localStartX + 2 * size - 1;
        int localEndY = localStartY + 2 * size - 1;

        log.info("Searching for ground items in tiles from ({}, {}) to ({}, {})", localStartX, localStartY, localEndX, localEndY);
        for (int tileX = Math.max(0, localStartX); tileX <= Math.min(localEndX, tiles[client.getPlane()].length - 1); tileX++) {
            for (int tileY = Math.max(0, localStartY); tileY <= Math.min(localEndY, tiles[client.getPlane()][tileX].length - 1); tileY++) {
                log.info("Checking tile: ({}, {})", tileX, tileY);
                Tile tile = tiles[client.getPlane()][tileX][tileY];
                if (tile != null && tile.getGroundItems() != null) {
                    for (TileItem groundItem : tile.getGroundItems()) {
                        ItemComposition itemComp = itemManager.getItemComposition(groundItem.getId());
                        String groundItemName = itemComp.getName();
                        if (groundItemName.equalsIgnoreCase(itemName) || itemName.isEmpty()) {
                            Map<String, Object> itemData = new HashMap<>();
                            itemData.put("name", groundItemName);
                            itemData.put("id", groundItem.getId());
                            WorldPoint worldPoint = tile.getWorldLocation();
                            Map<String, Integer> tileData = new HashMap<>();
                            tileData.put("x", worldPoint.getX());
                            tileData.put("y", worldPoint.getY());
                            tileData.put("plane", worldPoint.getPlane());
                            itemData.put("tile", tileData);

                            LocalPoint localPoint = tile.getLocalLocation();
                            Polygon tilePoly = Perspective.getCanvasTilePoly(client, localPoint);
                            if (tilePoly != null) {
                                Rectangle bounds = tilePoly.getBounds();
                                int centerX = (int) bounds.getCenterX();
                                int centerY = (int) bounds.getCenterY();
                                Map<String, Integer> middlePoint = new HashMap<>();
                                middlePoint.put("x", centerX);
                                middlePoint.put("y", centerY);
                                itemData.put("middle_point", middlePoint);
                            }

                            groundItemDataList.add(itemData);
                        }
                    }
                }
            }
        }
        return groundItemDataList;
    }
}