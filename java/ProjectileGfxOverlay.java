package net.runelite.client.plugins.asd;

import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.client.ui.overlay.Overlay;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayUtil;

import javax.inject.Inject;
import java.awt.*;

public class ProjectileGfxOverlay extends Overlay {

    private final Client client;
    private final AsdConfig config;

    @Inject
    public ProjectileGfxOverlay(Client client, AsdConfig config) {
        this.client = client;
        this.config = config;
        setPosition(OverlayPosition.DYNAMIC);
        setLayer(OverlayLayer.ABOVE_SCENE);
    }

    @Override
    public Dimension render(Graphics2D graphics) {
        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) return null;

        WorldPoint playerLoc = localPlayer.getWorldLocation();

        // === PROJECTILES ===
        if (config.projectilesEnabled()) {
            int radius = config.projectilesRadius();

            for (Projectile p : client.getProjectiles()) {
                if (p == null) continue;

                LocalPoint lp = new LocalPoint((int) p.getX(), (int) p.getY());
                WorldPoint projLoc = WorldPoint.fromLocal(client, lp);

                if (projLoc == null || projLoc.distanceTo(playerLoc) > radius) continue;

                net.runelite.api.Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane(), p.getHeight() / 2);
                if (screenPoint != null) {
                    String text = String.valueOf(p.getId());

                    OverlayUtil.renderTextLocation(graphics, screenPoint, text, Color.ORANGE);

                    graphics.setColor(Color.ORANGE);
                    graphics.fillRect(screenPoint.getX() - 2, screenPoint.getY() - 2, 4, 4);
                }
            }
        }

        // === GRAPHICS OBJECTS (GFX) ===
        if (config.graphicsObjectsEnabled()) {
            int radius = config.graphicsObjectsRadius();

            for (GraphicsObject gfx : client.getGraphicsObjects()) {
                if (gfx == null) continue;

                LocalPoint lp = gfx.getLocation();
                WorldPoint gfxLoc = WorldPoint.fromLocal(client, lp);

                if (gfxLoc == null || gfxLoc.distanceTo(playerLoc) > radius) continue;

                net.runelite.api.Point screenPoint = Perspective.localToCanvas(client, lp, client.getPlane());
                if (screenPoint != null) {
                    String text = String.valueOf(gfx.getId());

                    OverlayUtil.renderTextLocation(graphics, screenPoint, text, Color.CYAN);

                    graphics.setColor(Color.CYAN);
                    graphics.fillRect(screenPoint.getX() - 3, screenPoint.getY() - 3, 6, 6);
                }
            }
        }

        return null;
    }
}