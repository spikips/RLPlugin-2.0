package net.runelite.client.plugins.asd;

import net.runelite.api.Client;
import net.runelite.api.Perspective;
import net.runelite.api.Player;
import net.runelite.api.Point;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.client.ui.overlay.Overlay;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayUtil;

import javax.inject.Inject;
import java.awt.*;

public class PlayerOverlay extends Overlay {
    private final Client client;
    private final AsdConfig config;
    private final AsdPlugin plugin;

    @Inject
    private PlayerOverlay(Client client, AsdConfig config, AsdPlugin plugin) {
        this.client = client;
        this.config = config;
        this.plugin = plugin;
        setPosition(OverlayPosition.DYNAMIC);
        setLayer(OverlayLayer.ABOVE_SCENE);
    }

    // Updates to PlayerOverlay.java (update the render method for tile highlighting)
    @Override
    public Dimension render(Graphics2D graphics) {
        if (!config.playerHighlightEnabled()) {
            return null;
        }

        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) {
            return null;
        }

        WorldPoint localWorldPoint = localPlayer.getWorldLocation();
        int radius = config.playerRadius();

        // Save original font
        Font originalFont = graphics.getFont();

        // Set custom font size
        Font customFont = new Font("Arial", Font.PLAIN, config.playerTextSize());
        graphics.setFont(customFont);

        for (Player player : client.getPlayers()) {
            if (player == localPlayer || player.getName() == null) {
                continue;
            }

            WorldPoint playerWorldPoint = player.getWorldLocation();
            if (playerWorldPoint.distanceTo(localWorldPoint) > radius) {
                continue;
            }

            // Filter by name if specified
            String nameFilter = config.playerNameFilter().toLowerCase();
            if (!nameFilter.isEmpty() && !player.getName().toLowerCase().contains(nameFilter)) {
                continue;
            }

            LocalPoint localPoint = player.getLocalLocation();
            if (localPoint == null) {
                continue;
            }

            // Highlight outline
            if (config.highlightPlayerOutline()) {
                Shape hull = player.getConvexHull();
                if (hull != null) {
                    OverlayUtil.renderPolygon(graphics, hull, config.playerOutlineColor());
                }
            }

            // Highlight tile (using logical world location for snapping on ticks)
            if (config.highlightPlayerTile()) {
                int sceneX = playerWorldPoint.getX() - client.getBaseX();
                int sceneY = playerWorldPoint.getY() - client.getBaseY();
                LocalPoint lp = LocalPoint.fromScene(sceneX, sceneY);
                Polygon tilePoly = Perspective.getCanvasTilePoly(client, lp);
                if (tilePoly != null) {
                    OverlayUtil.renderPolygon(graphics, tilePoly, config.playerTileColor());
                }
            }

            // Show player info (centered above the player)
            if (config.showPlayerInfo()) {
                String info = String.format("%s (ID: %d, Combat: %d, Loc: %s)",
                        player.getName(), player.getId(), player.getCombatLevel(), playerWorldPoint.toString());

                // Use getCanvasTextLocation to get centered position
                Point textLocation = player.getCanvasTextLocation(graphics, info, player.getLogicalHeight() + 40);
                if (textLocation != null) {
                    OverlayUtil.renderTextLocation(graphics, textLocation, info, config.playerTextColor());
                }
            }
        }

        // Restore original font
        graphics.setFont(originalFont);

        return null;
    }
}