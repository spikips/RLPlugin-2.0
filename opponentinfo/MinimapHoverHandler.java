// File: MinimapHoverHandler.java
package net.runelite.client.plugins.asd;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.Point;
import net.runelite.api.Varbits;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.client.ui.overlay.OverlayManager;

import java.util.HashMap;
import java.util.Map;

import static net.runelite.api.Perspective.*;

@Slf4j
@Singleton
public class MinimapHoverHandler
{
    @Inject
    private Client client;

    @Inject
    private AsdConfig config;

    @Inject
    private OverlayManager overlayManager;

    @Inject
    private MinimapHoverOverlay minimapHoverOverlay;

    public Map<String, Object> handle(String function, Map<String, Object> params)
    {
        Map<String, Object> response = new HashMap<>();

        if (!config.enableMinimapHoverTile())
        {
            response.put("error", "Minimap hover tile display is disabled");
            return response;
        }

        switch (function)
        {
            case "minimapHoverTile":
                return getMinimapHoverTile(params);
            case "minimapTilePoint":
                return getMinimapTilePoint(params);
            default:
                response.put("error", "Unknown function: " + function);
                return response;
        }
    }

    private Map<String, Object> getMinimapHoverTile(Map<String, Object> params)
    {
        Map<String, Object> response = new HashMap<>();
        Point mousePos = client.getMouseCanvasPosition();

        // Check if mouse is over the minimap
        if (client.isInInstancedRegion())
        {
            response.put("error", "Minimap hover not supported in instanced regions");
            return response;
        }

        Widget minimapDrawWidget = getMinimapWidget();
        if (minimapDrawWidget == null || minimapDrawWidget.isHidden())
        {
            response.put("error", "Minimap widget not found");
            return response;
        }

        java.awt.Rectangle bounds = minimapDrawWidget.getBounds();
        java.awt.Point mouseAwt = new java.awt.Point(mousePos.getX(), mousePos.getY());
        if (!bounds.contains(mouseAwt))
        {
            response.put("error", "Mouse not over minimap");
            overlayManager.remove(minimapHoverOverlay);
            return response;
        }

        WorldPoint worldPoint = calculateMinimapTile(mousePos);
        if (worldPoint != null)
        {
            response.put("x", worldPoint.getX());
            response.put("y", worldPoint.getY());
            response.put("plane", worldPoint.getPlane());
            // Enable overlay rendering
            overlayManager.add(minimapHoverOverlay);
        }
        else
        {
            response.put("error", "Unable to calculate minimap tile");
            // Disable overlay if no valid tile
            overlayManager.remove(minimapHoverOverlay);
        }

        return response;
    }

    private Map<String, Object> getMinimapTilePoint(Map<String, Object> params)
    {
        Map<String, Object> response = new HashMap<>();

        if (!params.containsKey("x") || !params.containsKey("y")) {
            response.put("error", "Missing x or y parameters");
            return response;
        }

        int x = ((Number) params.get("x")).intValue();
        int y = ((Number) params.get("y")).intValue();
        int plane = params.containsKey("plane") ? ((Number) params.get("plane")).intValue() : client.getPlane();

        WorldPoint target = new WorldPoint(x, y, plane);
        Point point = calculateMinimapPoint(target);

        if (point != null) {
            response.put("x", point.getX());
            response.put("y", point.getY());
            response.put("zoom", client.getMinimapZoom());
        } else {
            response.put("error", "Unable to calculate minimap point (tile may not be loaded or visible)");
        }

        return response;
    }

    private Point calculateMinimapPoint(WorldPoint target)
    {
        LocalPoint targetLocal = LocalPoint.fromWorld(client, target);
        if (targetLocal == null) {
            return null;
        }

        LocalPoint playerLocal = client.getLocalPlayer().getLocalLocation();
        double dx = targetLocal.getX() - playerLocal.getX();
        double dy = targetLocal.getY() - playerLocal.getY();

        double pixelsPerTile = client.getMinimapZoom();
        double zoom = pixelsPerTile / LOCAL_TILE_SIZE;

        double mapX = dx * zoom;
        double mapY = dy * zoom;

        int angle = client.getCameraYawTarget() & 0x7FF;
        double sin = SINE[angle] / 65536.0;
        double cos = COSINE[angle] / 65536.0;

        // Inverse rotation
        double rx = cos * mapX + sin * mapY;
        double ry = sin * mapX - cos * mapY;

        Widget minimapWidget = getMinimapWidget();
        if (minimapWidget == null || minimapWidget.isHidden()) {
            return null;
        }

        int centerX = minimapWidget.getCanvasLocation().getX() + minimapWidget.getWidth() / 2;
        int centerY = minimapWidget.getCanvasLocation().getY() + minimapWidget.getHeight() / 2;

        int pointX = (int) (centerX + rx);
        int pointY = (int) (centerY + ry);

        // Optional: Check if point is within minimap bounds to avoid invalid clicks
        java.awt.Rectangle bounds = minimapWidget.getBounds();
        if (!bounds.contains(new java.awt.Point(pointX, pointY))) {
            return null;
        }

        return new Point(pointX, pointY);
    }

    private WorldPoint calculateMinimapTile(Point mousePos)
    {
        try
        {
            Widget minimapDrawWidget = getMinimapWidget();

            int centerX = minimapDrawWidget.getCanvasLocation().getX() + minimapDrawWidget.getWidth() / 2;
            int centerY = minimapDrawWidget.getCanvasLocation().getY() + minimapDrawWidget.getHeight() / 2;

            double rx = mousePos.getX() - centerX;
            double ry = mousePos.getY() - centerY;

            int angle = client.getCameraYawTarget() & 0x7FF;
            double sin = SINE[angle] / 65536.0;
            double cos = COSINE[angle] / 65536.0;

            double x = cos * rx + sin * ry;
            double y = sin * rx - cos * ry;

            double pixelsPerTile = client.getMinimapZoom();
            double zoom = pixelsPerTile / LOCAL_TILE_SIZE;

            double dx = x / zoom;
            double dy = y / zoom;

            LocalPoint playerLocal = client.getLocalPlayer().getLocalLocation();
            LocalPoint hoverLocal = new LocalPoint((int) (playerLocal.getX() + dx), (int) (playerLocal.getY() + dy));

            return WorldPoint.fromLocal(client, hoverLocal);
        }
        catch (Exception e)
        {
            log.error("Error calculating minimap tile: ", e);
            return null;
        }
    }

    private Widget getMinimapWidget()
    {
        if (client.isResized())
        {
            if (client.getVarbitValue(Varbits.SIDE_PANELS) == 1)
            {
                return client.getWidget(WidgetInfo.RESIZABLE_MINIMAP_DRAW_AREA);
            }
            else
            {
                return client.getWidget(WidgetInfo.RESIZABLE_MINIMAP_STONES_DRAW_AREA);
            }
        }
        else
        {
            return client.getWidget(WidgetInfo.FIXED_VIEWPORT_MINIMAP_DRAW_AREA);
        }
    }
}