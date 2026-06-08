package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Point;
import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.client.game.ItemManager;
import net.runelite.api.Projectile;
import net.runelite.api.GraphicsObject;
import javax.inject.Inject;
import java.awt.*;
import java.util.List;
import java.util.*;
import java.util.stream.Collectors;


@Slf4j
public class WorldHandler implements RequestHandler {
    @Inject
    private Client client;

    @Inject
    private ItemManager itemManager;

    @Inject
    private Gson gson;

    @Inject
    private AsdConfig config;

    @Override
    public Object handle(String function, Map<String, Object> params) {
        switch (function) {
            case "gameObject":
                return handleGameObjectRequest(params);
            case "tile":
                return handleTileRequest(params);
            case "walkable_tile":
                return handleWalkableTileRequest(params);
            case "minimapTiles":
                return handleMinimapTilesRequest(params);
            case "projectiles":
                return handleProjectilesRequest(params);
            case "graphics_objects":
            case "gfx":
                return handleGraphicsObjectsRequest(params);
            default:
                return new ResponseData().setError("Unknown world-related function: " + function);
        }
    }

    private List<Map<String, Object>> handleGameObjectRequest(Map<String, Object> params) {
        String objectFilterInput = ((String) params.getOrDefault("object", "")).toLowerCase();
        String[] objectFilters = objectFilterInput.isEmpty() ? new String[0] : objectFilterInput.split(",");
        Set<String> filterSet = Arrays.stream(objectFilters)
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toSet());

        boolean includeTile = Boolean.TRUE.equals(params.get("tile"));
        boolean includeMiddlePoint = params.containsKey("middle_point");
        int tileRadius = ((Number) params.getOrDefault("tile_radius",
                params.getOrDefault("radius", config.gameObjectRadius()))).intValue();

        List<Map<String, Object>> objectList = new ArrayList<>();
        Player player = client.getLocalPlayer();
        if (player == null) return objectList;

        WorldPoint playerLocation = player.getWorldLocation();
        Scene scene = client.getScene();
        int plane = client.getPlane();
        Tile[][] tiles = scene.getTiles()[plane];
        Random random = new Random();

        for (Tile[] tileRow : tiles) {
            for (Tile tile : tileRow) {
                if (tile == null) continue;
                if (tile.getWorldLocation().distanceTo(playerLocation) > tileRadius) continue;

                for (GameObject gameObject : tile.getGameObjects()) {
                    if (gameObject == null || gameObject.getId() == -1) continue;

                    ObjectComposition objectComp = client.getObjectDefinition(gameObject.getId());
                    if (objectComp == null || objectComp.getName() == null) continue;

                    String objectName = objectComp.getName().toLowerCase();
                    int objectId = gameObject.getId();
                    boolean matchesFilter = filterSet.isEmpty() || filterSet.stream().anyMatch(filter ->
                            objectName.contains(filter) || filter.equals(String.valueOf(objectId))
                    );

                    if (matchesFilter) {
                        Map<String, Object> objectData = new HashMap<>();
                        objectData.put("name", objectComp.getName());
                        objectData.put("id", gameObject.getId());
                        if (includeTile) {
                            WorldPoint objLocation = gameObject.getWorldLocation();
                            objectData.put("tile", Map.of(
                                    "x", objLocation.getX(),
                                    "y", objLocation.getY(),
                                    "plane", objLocation.getPlane()
                            ));
                        }
                        if (includeMiddlePoint) {
                            Shape convexHull = gameObject.getConvexHull();
                            if (convexHull != null) {
                                if (params.get("middle_point") == Boolean.FALSE) {
                                    Map<String, Integer> randomPoint = getRandomPointInShape(convexHull, random);
                                    if (randomPoint != null) {
                                        objectData.put("middle_point", randomPoint);
                                    }
                                } else {
                                    Rectangle bounds = convexHull.getBounds();
                                    int centerX = bounds.x + bounds.width / 2;
                                    int centerY = bounds.y + bounds.height / 2;
                                    objectData.put("middle_point", Map.of(
                                            "x", centerX,
                                            "y", centerY
                                    ));
                                }
                            } else {
                                // Fallback to original calculation if no convex hull
                                LocalPoint lp = gameObject.getLocalLocation();
                                Renderable renderable = gameObject.getRenderable();
                                int heightOffset = (renderable != null) ? renderable.getModelHeight() / 2 : 0;
                                Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane(), heightOffset);
                                if (screenPoint != null) {
                                    objectData.put("middle_point", Map.of(
                                            "x", screenPoint.getX(),
                                            "y", screenPoint.getY()
                                    ));
                                }
                            }
                        }
                        objectList.add(objectData);
                    }
                }
            }
        }
        return objectList;
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
            int x = minX + random.nextInt(maxX - minX);
            int y = minY + random.nextInt(maxY - minY);
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

    private List<Map<String, Object>> handleTileRequest(Map<String, Object> params) {
        int tileRadius = ((Double) params.getOrDefault("tile_radius", 0.0)).intValue();
        boolean includeMiddlePoint = params.containsKey("middle_point");
        Random random = new Random();

        List<Map<String, Object>> tileDataList = new ArrayList<>();
        WorldPoint playerTile = client.getLocalPlayer().getWorldLocation();
        WorldPoint centerTile = playerTile;

        Scene scene = client.getScene();
        Tile[][] tiles = scene.getTiles()[client.getPlane()];

        for (Tile[] tileRow : tiles) {
            for (Tile tile : tileRow) {
                if (tile == null) continue;

                WorldPoint tileLocation = tile.getWorldLocation();
                if (tileLocation.distanceTo(centerTile) > tileRadius) continue;

                Map<String, Object> tileData = new HashMap<>();
                tileData.put("x", tileLocation.getX());
                tileData.put("y", tileLocation.getY());
                tileData.put("plane", tileLocation.getPlane());

                if (includeMiddlePoint) {
                    LocalPoint lp = tile.getLocalLocation();
                    Polygon tilePoly = Perspective.getCanvasTilePoly(client, lp);
                    if (tilePoly != null) {
                        if (params.get("middle_point") == Boolean.FALSE) {
                            Map<String, Integer> randomPoint = getRandomPointInShape(tilePoly, random);
                            if (randomPoint != null) {
                                tileData.put("middle_point", randomPoint);
                            }
                        } else {
                            Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane(), 0);
                            if (screenPoint != null) {
                                tileData.put("middle_point", Map.of(
                                        "x", screenPoint.getX(),
                                        "y", screenPoint.getY()
                                ));
                            }
                        }
                    }
                }
                tileDataList.add(tileData);
            }
        }
        return tileDataList;
    }

    private List<Map<String, Object>> handleWalkableTileRequest(Map<String, Object> params) {
        int tileRadius = ((Double) params.getOrDefault("tile_radius", 0.0)).intValue();
        boolean includeMiddlePoint = params.containsKey("middle_point");
        Random random = new Random();

        List<Map<String, Object>> tileDataList = new ArrayList<>();
        WorldPoint playerTile = client.getLocalPlayer().getWorldLocation();
        WorldPoint centerTile = playerTile;

        Set<WorldPoint> reachableTiles = getReachableTiles(centerTile, tileRadius);
        for (WorldPoint tileLocation : reachableTiles) {
            Map<String, Object> tileData = new HashMap<>();
            tileData.put("x", tileLocation.getX());
            tileData.put("y", tileLocation.getY());
            tileData.put("plane", tileLocation.getPlane());

            if (includeMiddlePoint) {
                LocalPoint lp = LocalPoint.fromWorld(client, tileLocation);
                Polygon tilePoly = Perspective.getCanvasTilePoly(client, lp);
                if (tilePoly != null) {
                    if (params.get("middle_point") == Boolean.FALSE) {
                        Map<String, Integer> randomPoint = getRandomPointInShape(tilePoly, random);
                        if (randomPoint != null) {
                            tileData.put("middle_point", randomPoint);
                        }
                    } else {
                        Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane(), 0);
                        if (screenPoint != null) {
                            tileData.put("middle_point", Map.of(
                                    "x", screenPoint.getX(),
                                    "y", screenPoint.getY()
                            ));
                        }
                    }
                }
            }
            tileDataList.add(tileData);
        }
        return tileDataList;
    }

    private Set<WorldPoint> getReachableTiles(WorldPoint startTile, int radius) {
        Set<WorldPoint> reachableTiles = new HashSet<>();
        Queue<WorldPoint> queue = new LinkedList<>();
        Set<WorldPoint> visited = new HashSet<>();

        queue.add(startTile);
        visited.add(startTile);

        while (!queue.isEmpty()) {
            WorldPoint currentTile = queue.poll();
            if (currentTile.distanceTo(startTile) > radius) {
                continue;
            }
            reachableTiles.add(currentTile);

            for (int dx = -1; dx <= 1; dx++) {
                for (int dy = -1; dy <= 1; dy++) {
                    if (dx == 0 && dy == 0) continue;
                    WorldPoint neighbor = currentTile.dx(dx).dy(dy);

                    if (!visited.contains(neighbor) && canMoveTo(currentTile, neighbor)) {
                        queue.add(neighbor);
                        visited.add(neighbor);
                    }
                }
            }
        }
        return reachableTiles;
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
        if ((destCollisionFlags & CollisionDataFlag.BLOCK_MOVEMENT_FULL) != 0) {
            return false;
        }
        return true;
    }

    private int getCollisionFlagForDirection(int dx, int dy) {
        if (dx == -1 && dy == 0) {
            return CollisionDataFlag.BLOCK_MOVEMENT_WEST;
        } else if (dx == 1 && dy == 0) {
            return CollisionDataFlag.BLOCK_MOVEMENT_EAST;
        } else if (dx == 0 && dy == -1) {
            return CollisionDataFlag.BLOCK_MOVEMENT_SOUTH;
        } else if (dx == 0 && dy == 1) {
            return CollisionDataFlag.BLOCK_MOVEMENT_NORTH;
        } else {
            return 0;
        }
    }

    private Object handleMinimapTilesRequest(Map<String, Object> params) {
        Integer targetTileX = null;
        Integer targetTileY = null;

        if (params != null) {
            if (params.containsKey("tilex")) {
                targetTileX = ((Number) params.get("tilex")).intValue();
            }
            if (params.containsKey("tiley")) {
                targetTileY = ((Number) params.get("tiley")).intValue();
            }
        }

        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) {
            return Collections.emptyList();
        }

        if (client.getGameState() != GameState.LOGGED_IN) {
            return Collections.emptyList();
        }

        WorldPoint playerPosition = localPlayer.getWorldLocation();
        int radius = 18;

        List<Map<String, Integer>> visibleTiles = new ArrayList<>();

        for (int dx = -radius; dx <= radius; dx++) {
            for (int dy = -radius; dy <= radius; dy++) {
                int x = playerPosition.getX() + dx;
                int y = playerPosition.getY() + dy;
                int plane = playerPosition.getPlane();

                if (targetTileX != null && targetTileY != null && (x != targetTileX || y != targetTileY)) {
                    continue;
                }

                WorldPoint tileWorldPoint = new WorldPoint(x, y, plane);
                LocalPoint tileLocalPoint = LocalPoint.fromWorld(client, tileWorldPoint);
                if (tileLocalPoint == null) {
                    continue;
                }

                Point minimapPoint = Perspective.localToMinimap(client, tileLocalPoint);
                if (minimapPoint == null) {
                    continue;
                }

                int distanceSq = dx * dx + dy * dy;
                if (distanceSq <= radius * radius) {
                    Map<String, Integer> tileInfo = new HashMap<>();
                    tileInfo.put("tileX", x);
                    tileInfo.put("tileY", y);
                    tileInfo.put("clientX", minimapPoint.getX());
                    tileInfo.put("clientY", minimapPoint.getY());
                    visibleTiles.add(tileInfo);

                    if (targetTileX != null && targetTileY != null) {
                        return visibleTiles;
                    }
                }
            }
        }

        return visibleTiles;
    }

    private List<Map<String, Object>> handleProjectilesRequest(Map<String, Object> params) {
        String idFilter = (String) params.getOrDefault("id", "");
        int radius = params.containsKey("radius")
                ? ((Number) params.get("radius")).intValue()
                : 35;

        boolean includeMiddlePoint = Boolean.TRUE.equals(params.getOrDefault("middle_point", true));

        List<Map<String, Object>> projList = new ArrayList<>();
        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) return projList;

        WorldPoint playerLoc = localPlayer.getWorldLocation();

        for (Projectile p : client.getProjectiles()) {
            if (p == null) continue;

            LocalPoint lp = new LocalPoint((int) p.getX(), (int) p.getY());
            WorldPoint projWorld = WorldPoint.fromLocal(client, lp);
            if (projWorld == null || projWorld.distanceTo(playerLoc) > radius) continue;

            if (!idFilter.isEmpty() && !String.valueOf(p.getId()).equals(idFilter)) continue;

            Map<String, Object> data = new HashMap<>();
            data.put("id", p.getId());
            data.put("remainingCycles", p.getRemainingCycles());
            data.put("height", p.getHeight());

            if (p.getInteracting() != null) {
                Actor target = p.getInteracting();
                data.put("targetName", target.getName());

                if (target instanceof NPC) {
                    data.put("targetIndex", ((NPC) target).getIndex());
                    data.put("targetType", "npc");
                } else if (target instanceof Player) {
                    data.put("targetId", ((Player) target).getId());
                    data.put("targetType", "player");
                } else {
                    data.put("targetType", "other");
                }
            }

            data.put("tile", Map.of("x", projWorld.getX(), "y", projWorld.getY(), "plane", projWorld.getPlane()));

            if (includeMiddlePoint) {
                Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane(), (int) (p.getHeight() / 2));
                if (screenPoint != null) {
                    data.put("middle_point", Map.of("x", screenPoint.getX(), "y", screenPoint.getY()));
                }
            }
            projList.add(data);
        }
        return projList;
    }

    private List<Map<String, Object>> handleGraphicsObjectsRequest(Map<String, Object> params) {
        String idFilter = (String) params.getOrDefault("id", "");
        int radius = params.containsKey("radius")
                ? ((Number) params.get("radius")).intValue()
                : 20;

        boolean includeMiddlePoint = Boolean.TRUE.equals(params.getOrDefault("middle_point", true));

        List<Map<String, Object>> gfxList = new ArrayList<>();
        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) return gfxList;

        WorldPoint playerLoc = localPlayer.getWorldLocation();

        for (GraphicsObject gfx : client.getGraphicsObjects()) {
            if (gfx == null) continue;

            LocalPoint lp = gfx.getLocation();
            WorldPoint gfxWorld = WorldPoint.fromLocal(client, lp);
            if (gfxWorld == null || gfxWorld.distanceTo(playerLoc) > radius) continue;

            if (!idFilter.isEmpty() && !String.valueOf(gfx.getId()).equals(idFilter)) continue;

            Map<String, Object> data = new HashMap<>();
            data.put("id", gfx.getId());
            data.put("tile", Map.of("x", gfxWorld.getX(), "y", gfxWorld.getY(), "plane", gfxWorld.getPlane()));

            if (includeMiddlePoint) {
                Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane());
                if (screenPoint != null) {
                    data.put("middle_point", Map.of("x", screenPoint.getX(), "y", screenPoint.getY()));
                }
            }
            gfxList.add(data);
        }
        return gfxList;
    }
}