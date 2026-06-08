package net.runelite.client.plugins.asd;

import net.runelite.api.Client;
import net.runelite.api.NPC;
import net.runelite.api.NPCComposition;
import net.runelite.api.Player;
import net.runelite.api.coords.WorldPoint;
import net.runelite.client.ui.overlay.Overlay;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPosition;
import javax.inject.Inject;
import java.awt.*;
import java.awt.geom.Rectangle2D;
import java.util.List;

public class NpcOverlay extends Overlay {

    private final Client client;
    private final AsdConfig config;

    @Inject
    public NpcOverlay(Client client, AsdConfig config) {
        this.client = client;
        this.config = config;

        setPosition(OverlayPosition.DYNAMIC);
        setLayer(OverlayLayer.ABOVE_SCENE);
    }

    @Override
    public Dimension render(Graphics2D graphics) {
        if (!config.npcHighlightEnabled()) {
            return null;
        }

        Player localPlayer = client.getLocalPlayer();
        if (localPlayer == null) return null;

        WorldPoint playerLoc = localPlayer.getWorldLocation();

        List<NPC> npcs = client.getNpcs();

        graphics.setFont(new Font("Arial", Font.PLAIN, config.npcTextSize()));
        FontMetrics fontMetrics = graphics.getFontMetrics();

        String filterInput = config.npcNameFilter().toLowerCase();
        String[] filters = filterInput.isEmpty() ? new String[0] : filterInput.split(",");

        for (NPC npc : npcs) {
            NPCComposition composition = npc.getComposition();

            if (composition == null || composition.getName() == null || composition.getName().isEmpty()) {
                continue;
            }

            String npcNameLower = composition.getName().toLowerCase();
            int npcId = npc.getId();

            boolean matchesFilter = filters.length == 0;
            if (filters.length > 0) {
                matchesFilter = false;
                for (String filter : filters) {
                    if (!filter.trim().isEmpty() &&
                            (npcNameLower.contains(filter.trim()) ||
                                    filter.trim().equals(String.valueOf(npcId)))) {
                        matchesFilter = true;
                        break;
                    }
                }
            }

            if (!matchesFilter) continue;

            // Respect new npcRadius config
            if (npc.getWorldLocation().distanceTo(playerLoc) > config.npcRadius()) {
                continue;
            }

            if (config.showNPCInfo()) {
                String text = String.format("%s (ID: %d)", composition.getName(), npcId);

                WorldPoint npcWorldPoint = npc.getWorldLocation();
                int npcSize = composition.getSize();
                WorldPoint neTile = npcWorldPoint;

                if (npcSize > 1) {
                    neTile = new WorldPoint(
                            npcWorldPoint.getX() + (npcSize - 1),
                            npcWorldPoint.getY() + (npcSize - 1),
                            npcWorldPoint.getPlane()
                    );
                }
                text += String.format(" NE Tile: [%d, %d]", neTile.getX(), neTile.getY());

                Shape npcShape = npc.getConvexHull();
                if (npcShape != null) {
                    Rectangle2D npcBounds = npcShape.getBounds2D();
                    int centerX = (int) npcBounds.getCenterX();
                    int npcHeight = (int) npcBounds.getHeight();
                    int middleY = (int) (npcBounds.getY() + npcHeight / 2);

                    text += String.format(" Screen: [%d, %d]", centerX, middleY);

                    int animationId = npc.getAnimation();
                    String animationText = animationId != -1 ?
                            String.format(" Animation: %d", animationId) : " Animation: None";
                    text += animationText;

                    System.out.printf("Middle Point: [X: %d, Y: %d]%n", centerX, middleY);

                    int textWidth = fontMetrics.stringWidth(text);

                    int textX = centerX - textWidth / 2;
                    int textY = (int) npcBounds.getY() - 5;

                    graphics.setColor(Color.BLACK);
                    graphics.drawString(text, textX + 1, textY + 1);

                    graphics.setColor(config.npcTextColor());
                    graphics.drawString(text, textX, textY);

                    System.out.printf("NPC: %s%n", text);
                }
            }

            if (config.highlightNPCOutline() && matchesFilter) {
                Shape npcHull = npc.getConvexHull();
                if (npcHull != null) {
                    graphics.setColor(config.npcOutlineColor());
                    graphics.draw(npcHull);
                }
            }
        }

        return null;
    }
}