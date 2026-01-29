package net.runelite.client.plugins.opponentinfo;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.FontMetrics;
import java.awt.Shape;
import javax.inject.Inject;
import net.runelite.api.Actor;
import net.runelite.api.Client;
import net.runelite.api.NPC;
import net.runelite.api.Perspective;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.client.ui.overlay.Overlay;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayPriority;

public class CustomOpponentInfoOverlay extends Overlay {
    private final Client client;
    private final CustomOpponentInfoPlugin plugin;
    private final CustomOpponentInfoConfig config;

    @Inject
    public CustomOpponentInfoOverlay(Client client, CustomOpponentInfoPlugin plugin, CustomOpponentInfoConfig config) {
        this.client = client;
        this.plugin = plugin;
        this.config = config;
        setPosition(OverlayPosition.DYNAMIC);
        setLayer(OverlayLayer.ABOVE_SCENE);
        setPriority(OverlayPriority.HIGH);
    }

    @Override
    public Dimension render(Graphics2D graphics) {
        Actor opponent = plugin.getLastOpponent();
        if (opponent instanceof NPC) {
            NPC npc = (NPC) opponent;
            renderNpcOverlay(graphics, npc);
        }
        return null;
    }

    private void renderNpcOverlay(Graphics2D graphics, NPC npc) {
        int health = (int) Math.round(npc.getHealthRatio() / 4.0);
        String healthText = "HP: " + health;

        LocalPoint localPoint = npc.getLocalLocation();
        net.runelite.api.Point canvasPoint = Perspective.localToCanvas(client, localPoint, client.getPlane(), npc.getLogicalHeight() + 40);
        if (canvasPoint != null) {
            int baseX = canvasPoint.getX();
            int baseY = canvasPoint.getY();

            FontMetrics metrics = graphics.getFontMetrics();

            // Draw the text
            graphics.setColor(Color.WHITE);
            drawTextWithShadow(graphics, healthText, baseX + 2, baseY - (2 * metrics.getHeight()) + metrics.getAscent());

            if (config.showAnimationId()) {
                String animationId = "Anim: " + npc.getAnimation();
                drawTextWithShadow(graphics, animationId, baseX + 2, baseY - metrics.getHeight() + metrics.getAscent());
            }

            if (config.showTileInfo()) {
                WorldPoint worldPoint = WorldPoint.fromLocal(client, localPoint);
                String tileLocation = "Tile: " + worldPoint.getX() + ", " + worldPoint.getY();
                drawTextWithShadow(graphics, tileLocation, baseX + 2, baseY + metrics.getAscent());
            }
        }

        highlightNpc(graphics, npc);
    }

    private void highlightNpc(Graphics2D graphics, NPC npc) {
        if (config.highlightNPCOutline()) {
            Shape npcHull = npc.getConvexHull();
            if (npcHull != null) {
                graphics.setColor(config.npcOutlineColor());
                graphics.draw(npcHull);
            }
        }
    }

    private void drawTextWithShadow(Graphics2D graphics, String text, int x, int y) {
        graphics.setColor(Color.BLACK);
        graphics.drawString(text, x + 1, y + 1);
        graphics.drawString(text, x - 1, y - 1);
        graphics.drawString(text, x + 1, y - 1);
        graphics.drawString(text, x - 1, y + 1);
        graphics.setColor(Color.WHITE);
        graphics.drawString(text, x, y);
    }
}
