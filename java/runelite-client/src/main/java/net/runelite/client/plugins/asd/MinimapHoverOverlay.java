// File: MinimapHoverOverlay.java
package net.runelite.client.plugins.asd;

import com.google.inject.Inject;
import net.runelite.api.Client;
import net.runelite.api.Point;
import net.runelite.client.ui.overlay.Overlay;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayPriority;

import java.awt.*;
import java.util.HashMap;
import java.util.Map;

public class MinimapHoverOverlay extends Overlay
{
    @Inject
    private Client client;

    @Inject
    private AsdConfig config;

    @Inject
    private MinimapHoverHandler minimapHoverHandler;

    public MinimapHoverOverlay()
    {
        setPosition(OverlayPosition.DYNAMIC);
        setLayer(OverlayLayer.ABOVE_WIDGETS);
        setPriority(OverlayPriority.HIGH);
    }

    @Override
    public Dimension render(Graphics2D graphics)
    {
        if (!config.enableMinimapHoverTile())
        {
            return null;
        }

        Point mousePos = client.getMouseCanvasPosition();
        Map<String, Object> tileData = minimapHoverHandler.handle("minimapHoverTile", new HashMap<>());

        if (!tileData.containsKey("error"))
        {
            int x = ((Number) tileData.get("x")).intValue();
            int y = ((Number) tileData.get("y")).intValue();
            int plane = ((Number) tileData.get("plane")).intValue();
            String text = String.format("(%d, %d, %d)", x, y, plane);

            // Set font and shadow
            graphics.setFont(new Font("Arial", Font.PLAIN, config.minimapHoverTextSize()));
            graphics.setColor(config.minimapHoverTextShadowColor());
            graphics.drawString(text, mousePos.getX() + 10 + 1, mousePos.getY() - 5 + 1); // Shadow offset
            graphics.setColor(config.minimapHoverTextColor());
            graphics.drawString(text, mousePos.getX() + 10, mousePos.getY() - 5); // Main text
        }

        return null;
    }
}