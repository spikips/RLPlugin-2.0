package net.runelite.client.plugins.asd;

import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.GameObject;
import net.runelite.api.Tile;
import net.runelite.api.events.AnimationChanged;
import net.runelite.api.events.GameObjectSpawned;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.Point;
import net.runelite.api.Perspective;
import net.runelite.api.Renderable;
import net.runelite.client.eventbus.Subscribe;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Singleton
public class CannonHandler {

    @Inject
    private Client client;

    private WorldPoint cannonPosition = null;
    private long lastPlacementTick = -1;

    private static final int CANNON_BASE_ID = 6;
    private static final int PLACEMENT_ANIMATION = 827;

    @Subscribe
    public void onAnimationChanged(AnimationChanged event) {
        if (event.getActor() == client.getLocalPlayer() && event.getActor().getAnimation() == PLACEMENT_ANIMATION) {
            lastPlacementTick = client.getTickCount();
            log.debug("Player placing cannon detected (animation 827)");
        }
    }

    @Subscribe
    public void onGameObjectSpawned(GameObjectSpawned event) {
        GameObject obj = event.getGameObject();
        if (obj.getId() == CANNON_BASE_ID && client.getTickCount() - lastPlacementTick <= 2) {
            cannonPosition = obj.getWorldLocation();
            log.info("Your cannon placed at {}", cannonPosition);
        }
    }

    public Map<String, Object> getCannonData() {
        Map<String, Object> data = new HashMap<>();

        if (cannonPosition == null) {
            data.put("exists", false);
            data.put("position", null);
            data.put("id", -1);
            data.put("ammo", client.getVarpValue(3));  // Using VarPlayer 3 as per your observation
            return data;
        }

        data.put("exists", true);
        data.put("position", cannonPosition.toString());

        int currentId = -1;
        int ammo = client.getVarpValue(3);
        Map<String, Integer> mp = null;

        int plane = cannonPosition.getPlane();
        int localX = cannonPosition.getX() - client.getBaseX();
        int localY = cannonPosition.getY() - client.getBaseY();

        Tile[][][] tiles = client.getScene().getTiles();
        if (plane < tiles.length && localX >= 0 && localX < tiles[plane].length && localY >= 0 && localY < tiles[plane][localX].length) {
            Tile tile = tiles[plane][localX][localY];
            if (tile != null) {
                for (GameObject obj : tile.getGameObjects()) {
                    if (obj != null && obj.getId() >= 6 && obj.getId() <= 9) {
                        currentId = obj.getId();
                        Renderable renderable = obj.getRenderable();
                        if (renderable != null) {
                            LocalPoint lp = obj.getLocalLocation();
                            if (lp != null) {
                                Point canvasPoint = Perspective.localToCanvas(client, lp, plane, renderable.getModelHeight() / 2);
                                if (canvasPoint != null) {
                                    mp = new HashMap<>();
                                    mp.put("x", canvasPoint.getX());
                                    mp.put("y", canvasPoint.getY());
                                }
                            }
                        }
                        break;
                    }
                }
            }
        }

        data.put("id", currentId);
        data.put("ammo", ammo);
        data.put("middle_point", mp);

        return data;
    }

    public void resetCannon() {
        log.info("Cannon tracking RESET called - clearing position and timestamp");
        cannonPosition = null;
        lastPlacementTick = -1;
    }
}