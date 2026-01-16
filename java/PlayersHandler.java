package net.runelite.client.plugins.asd;

import net.runelite.api.Client;
import net.runelite.api.Player;
import net.runelite.api.coords.WorldPoint;

import javax.inject.Inject;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PlayersHandler {
    @Inject
    private Client client;

    public Object handle(String function, Map<String, Object> params) {
        if (!"players".equals(function)) {
            return null;
        }

        int radius = params.containsKey("radius") ? ((Number) params.get("radius")).intValue() : 10;
        String nameFilter = params.containsKey("name") ? (String) params.get("name") : "";

        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) {
            return new ArrayList<>();
        }

        WorldPoint localWorldPoint = localPlayer.getWorldLocation();
        List<Map<String, Object>> playersData = new ArrayList<>();

        for (Player player : client.getPlayers()) {
            if (player == localPlayer || player.getName() == null) {
                continue;
            }

            WorldPoint playerWorldPoint = player.getWorldLocation();
            if (playerWorldPoint.distanceTo(localWorldPoint) > radius) {
                continue;
            }

            // Filter by name if provided
            if (!nameFilter.isEmpty() && !player.getName().toLowerCase().contains(nameFilter.toLowerCase())) {
                continue;
            }

            Map<String, Object> data = new HashMap<>();
            data.put("name", player.getName());
            data.put("id", player.getId());
            data.put("combatLevel", player.getCombatLevel());
            data.put("location", playerWorldPoint.toString());
            data.put("animation", player.getAnimation());
            data.put("healthRatio", player.getHealthRatio());
            data.put("isInteracting", player.getInteracting() != null);

            playersData.add(data);
        }

        return playersData;
    }
}