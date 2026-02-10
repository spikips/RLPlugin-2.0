package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.*;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.client.game.ItemManager;

import javax.inject.Inject;
import java.awt.Point;
import java.awt.*;
import java.util.List;
import java.util.*;

@Slf4j
public class InterfaceHandler implements RequestHandler {
    @Inject
    private Client client;

    @Inject
    private ItemManager itemManager;

    @Inject
    private Gson gson;

    @Override
    public Object handle(String function, Map<String, Object> params) {
        switch (function) {
            case "inventory":
                return handleInventoryRequest(params);
            case "bankItems":
                return handleBankItemsRequest(params);
            case "clickWidget":
                return handleClickWidgetRequest(params);
            case "interactOptions":
                return handleInteractOptionsRequest();
            default:
                return new ResponseData().setError("Unknown interface-related function: " + function);
        }
    }

    private Object handleInventoryRequest(Map<String, Object> params) {
        String itemFilter = (String) params.getOrDefault("item", "");
        boolean includeMiddlePoint = (boolean) params.getOrDefault("middle_point", false);
        List<Map<String, Object>> inventoryData = new ArrayList<>();
        Random random = new Random();

        ItemContainer inventory = client.getItemContainer(InventoryID.INVENTORY);
        if (inventory == null) return inventoryData;

        Item[] items = inventory.getItems();

        Widget bankWidget = client.getWidget(WidgetInfo.BANK_CONTAINER);
        boolean isBankOpen = bankWidget != null && !bankWidget.isHidden();

        Widget inventoryWidget;
        if (isBankOpen) {
            inventoryWidget = client.getWidget(WidgetInfo.BANK_INVENTORY_ITEMS_CONTAINER);
        } else {
            inventoryWidget = client.getWidget(WidgetInfo.INVENTORY);
        }

        boolean widgetVisible = inventoryWidget != null && !inventoryWidget.isHidden();

        Widget[] itemWidgets = widgetVisible ? inventoryWidget.getDynamicChildren() : new Widget[0];

        for (int i = 0; i < items.length; i++) {
            Item item = items[i];
            if (item.getId() <= 0) continue;

            ItemComposition itemComp = itemManager.getItemComposition(item.getId());
            String itemName = itemComp.getName();
            boolean matchesFilter = itemFilter.isEmpty()
                    || itemName.toLowerCase().contains(itemFilter.toLowerCase())
                    || String.valueOf(item.getId()).equals(itemFilter);

            if (matchesFilter) {
                Map<String, Object> itemData = new HashMap<>();
                itemData.put("name", itemName);
                itemData.put("id", item.getId());

                if (includeMiddlePoint && widgetVisible && i < itemWidgets.length) {
                    Widget itemWidget = itemWidgets[i];
                    net.runelite.api.Point itemLocation = itemWidget.getCanvasLocation();
                    if (itemLocation != null) {
                        int centerX = itemLocation.getX() + itemWidget.getWidth() / 2;
                        int centerY = itemLocation.getY() + itemWidget.getHeight() / 2;
                        itemData.put("middle_point", Map.of("x", centerX, "y", centerY));

                        Map<String, Integer> randomPoint = getRandomPointInRectangle(
                                itemLocation.getX(), itemLocation.getY(),
                                itemWidget.getWidth(), itemWidget.getHeight(), random);
                        if (randomPoint != null) {
                            itemData.put("random_clickpoint", randomPoint);
                        }
                    }
                }

                inventoryData.add(itemData);
            }
        }
        return inventoryData;
    }

    private Map<String, Integer> getRandomPointInRectangle(int x, int y, int width, int height, Random random) {
        if (width <= 0 || height <= 0) {
            return null;
        }
        int inset = 2;
        if (width <= 2 * inset || height <= 2 * inset) {
            return Map.of("x", x + width / 2, "y", y + height / 2);
        }
        int randX = x + inset + random.nextInt(width - 2 * inset);
        int randY = y + inset + random.nextInt(height - 2 * inset);
        return Map.of("x", randX, "y", randY);
    }

    private Object handleBankItemsRequest(Map<String, Object> params) {
        List<Map<String, Object>> bankItems = new ArrayList<>();
        String itemFilter = (String) params.getOrDefault("item", "");

        // Hardcode the new bank item container ID (786444)
        Widget bankWidget = client.getWidget(786444);

        // Optional: fallback to group/child if preferred
        // Widget bankWidget = client.getWidget(12, 12);

        if (bankWidget == null || bankWidget.isHidden() || bankWidget.getDynamicChildren() == null) {
            log.warn("Bank data requested but bank interface is not open or container not found.");
            return bankItems;
        }
        Random random = new Random();

        for (Widget itemWidget : bankWidget.getDynamicChildren()) {
            if (itemWidget == null || itemWidget.getItemId() <= 0) continue;

            // Rest of the code remains exactly the same...
            int itemId = itemWidget.getItemId();
            ItemComposition itemComp = itemManager.getItemComposition(itemId);
            String itemName = itemComp != null ? itemComp.getName() : "Unknown";
            int quantity = itemWidget.getItemQuantity();

            boolean matchesFilter = itemFilter.isEmpty()
                    || itemName.toLowerCase().contains(itemFilter.toLowerCase())
                    || String.valueOf(itemId).equals(itemFilter);

            if (matchesFilter) {
                Map<String, Object> itemData = new HashMap<>();
                itemData.put("name", itemName);
                itemData.put("id", itemId);
                itemData.put("quantity", quantity);

                net.runelite.api.Point canvasLocation = itemWidget.getCanvasLocation();
                if (canvasLocation != null) {
                    int centerX = canvasLocation.getX() + itemWidget.getWidth() / 2;
                    int centerY = canvasLocation.getY() + itemWidget.getHeight() / 2;
                    itemData.put("middle_point", Map.of("x", centerX, "y", centerY));

                    Map<String, Integer> randomPoint = getRandomPointInRectangle(
                            canvasLocation.getX(), canvasLocation.getY(),
                            itemWidget.getWidth(), itemWidget.getHeight(), random);
                    if (randomPoint != null) {
                        itemData.put("random_clickpoint", randomPoint);
                    }
                }
                bankItems.add(itemData);
            }
        }
        return bankItems;
    }


    // Updated handleClickWidgetRequest in InterfaceHandler.java (separate "name" and "text"; apply to widget and children; add textColor)
    private Object handleClickWidgetRequest(Map<String, Object> params) {
        Map<String, Object> widgetData = new HashMap<>();
        if (params == null || (!params.containsKey("x") && !params.containsKey("y"))) {
            List<Map<String, Object>> allWidgets = new ArrayList<>();
            Random random = new Random();
            for (int groupId = 0; groupId < 1000; groupId++) { // Increased to cover spellbook group 548 etc.
                for (int childId = 0; childId < 2000; childId++) { // Increased for safety
                    Widget widget = client.getWidget(groupId, childId);
                    if (widget != null && !widget.isHidden()) {
                        Map<String, Object> widgetInfo = new HashMap<>();
                        widgetInfo.put("id", widget.getId());
                        widgetInfo.put("name", widget.getName() != null ? widget.getName() : ""); // New: Separate name
                        widgetInfo.put("text", widget.getText() != null ? widget.getText() : ""); // Separate text
                        widgetInfo.put("textColor", widget.getTextColor()); // New: textColor
                        widgetInfo.put("hasOnOpListener", widget.getOnOpListener() != null);
                        widgetInfo.put("enabled", widget.getOnOpListener() == null);
                        Object[] onOpListener = widget.getOnOpListener();
                        if (onOpListener != null) {
                            List<Object> onOpListenerList = new ArrayList<>();
                            for (Object obj : onOpListener) {
                                if (obj instanceof Number) {
                                    onOpListenerList.add(((Number) obj).longValue());
                                } else if (obj != null) {
                                    onOpListenerList.add(obj.toString());
                                } else {
                                    onOpListenerList.add(null);
                                }
                            }
                            widgetInfo.put("OnOpListener", onOpListenerList);
                        } else {
                            widgetInfo.put("OnOpListener", null);
                        }
                        Rectangle bounds = widget.getBounds();
                        if (bounds != null) {
                            Map<String, Integer> boundInfo = new HashMap<>();
                            boundInfo.put("x", bounds.x);
                            boundInfo.put("y", bounds.y);
                            boundInfo.put("width", bounds.width);
                            boundInfo.put("height", bounds.height);
                            widgetInfo.put("bounds", boundInfo);
                            if (bounds.width > 0 && bounds.height > 0) {
                                Map<String, Integer> randomPoint = getRandomPointInRectangle(
                                        bounds.x, bounds.y,
                                        bounds.width, bounds.height, random);
                                if (randomPoint != null) {
                                    widgetInfo.put("random_clickpoint", randomPoint);
                                }
                            }
                        }
                        widgetInfo.put("spriteId", widget.getSpriteId());
                        if (widget.getDynamicChildren() != null) {
                            List<Map<String, Object>> children = new ArrayList<>();
                            for (Widget child : widget.getDynamicChildren()) {
                                Map<String, Object> childInfo = new HashMap<>();
                                childInfo.put("id", child.getId());
                                childInfo.put("name", child.getName() != null ? child.getName() : ""); // New: Separate name for children
                                childInfo.put("text", child.getText() != null ? child.getText() : ""); // Separate text for children
                                childInfo.put("textColor", child.getTextColor()); // New: textColor for children
                                childInfo.put("hasOnOpListener", child.getOnOpListener() != null);
                                childInfo.put("enabled", child.getOnOpListener() == null);
                                Object[] childOnOpListener = child.getOnOpListener();
                                if (childOnOpListener != null) {
                                    List<Object> childOnOpListenerList = new ArrayList<>();
                                    for (Object obj : childOnOpListener) {
                                        if (obj instanceof Number) {
                                            childOnOpListenerList.add(((Number) obj).longValue());
                                        } else if (obj != null) {
                                            childOnOpListenerList.add(obj.toString());
                                        } else {
                                            childOnOpListenerList.add(null);
                                        }
                                    }
                                    childInfo.put("OnOpListener", childOnOpListenerList);
                                } else {
                                    childInfo.put("OnOpListener", null);
                                }
                                if (child.getItemId() > 0) {
                                    childInfo.put("itemId", child.getItemId());
                                    childInfo.put("quantity", child.getItemQuantity());
                                }
                                childInfo.put("spriteId", child.getSpriteId());
                                Rectangle childBounds = child.getBounds();
                                if (childBounds != null) {
                                    Map<String, Integer> childBoundInfo = new HashMap<>();
                                    childBoundInfo.put("x", childBounds.x);
                                    childBoundInfo.put("y", childBounds.y);
                                    childBoundInfo.put("width", childBounds.width);
                                    childBoundInfo.put("height", childBounds.height);
                                    childInfo.put("bounds", childBoundInfo);
                                    if (childBounds.width > 0 && childBounds.height > 0) {
                                        Map<String, Integer> childRandomPoint = getRandomPointInRectangle(
                                                childBounds.x, childBounds.y,
                                                childBounds.width, childBounds.height, random);
                                        if (childRandomPoint != null) {
                                            childInfo.put("random_clickpoint", childRandomPoint);
                                        }
                                    }
                                }
                                children.add(childInfo);
                            }
                            widgetInfo.put("children", children);
                        } else {
                            widgetInfo.put("children", new ArrayList<>());
                        }
                        allWidgets.add(widgetInfo);
                    }
                }
            }
            widgetData.put("widgets", allWidgets);
            log.debug("Returned all visible widgets: {}", allWidgets.size());
            return widgetData;
        }
        int x = ((Number) params.get("x")).intValue();
        int y = ((Number) params.get("y")).intValue();
        java.awt.Point clickPoint = new java.awt.Point(x, y);
        Widget widget = findWidgetAtPoint(clickPoint);
        if (widget != null) {
            Map<String, Object> widgetInfo = new HashMap<>();
            widgetInfo.put("id", widget.getId());
            widgetInfo.put("name", widget.getName() != null ? widget.getName() : ""); // New: Separate name
            widgetInfo.put("text", widget.getText() != null ? widget.getText() : ""); // Separate text
            widgetInfo.put("textColor", widget.getTextColor()); // New: textColor
            widgetInfo.put("hasOnOpListener", widget.getOnOpListener() != null);
            widgetInfo.put("enabled", widget.getOnOpListener() == null);
            Object[] onOpListener = widget.getOnOpListener();
            if (onOpListener != null) {
                List<Object> onOpListenerList = new ArrayList<>();
                for (Object obj : onOpListener) {
                    if (obj instanceof Number) {
                        onOpListenerList.add(((Number) obj).longValue());
                    } else if (obj != null) {
                        onOpListenerList.add(obj.toString());
                    } else {
                        onOpListenerList.add(null);
                    }
                }
                widgetInfo.put("OnOpListener", onOpListenerList);
            } else {
                widgetInfo.put("OnOpListener", null);
            }
            Rectangle bounds = widget.getBounds();
            if (bounds != null) {
                Map<String, Integer> boundInfo = new HashMap<>();
                boundInfo.put("x", bounds.x);
                boundInfo.put("y", bounds.y);
                boundInfo.put("width", bounds.width);
                boundInfo.put("height", bounds.height);
                widgetInfo.put("bounds", boundInfo);
                if (bounds.width > 0 && bounds.height > 0) {
                    Random random = new Random();
                    Map<String, Integer> randomPoint = getRandomPointInRectangle(
                            bounds.x, bounds.y,
                            bounds.width, bounds.height, random);
                    if (randomPoint != null) {
                        widgetInfo.put("random_clickpoint", randomPoint);
                    }
                }
            }
            widgetInfo.put("spriteId", widget.getSpriteId());
            if (widget.getDynamicChildren() != null) {
                List<Map<String, Object>> children = new ArrayList<>();
                Random random = new Random();
                for (Widget child : widget.getDynamicChildren()) {
                    Map<String, Object> childInfo = new HashMap<>();
                    childInfo.put("id", child.getId());
                    childInfo.put("name", child.getName() != null ? child.getName() : ""); // New: Separate name for children
                    childInfo.put("text", child.getText() != null ? child.getText() : ""); // Separate text for children
                    childInfo.put("textColor", child.getTextColor()); // New: textColor for children
                    childInfo.put("hasOnOpListener", child.getOnOpListener() != null);
                    childInfo.put("enabled", child.getOnOpListener() == null);
                    Object[] childOnOpListener = child.getOnOpListener();
                    if (childOnOpListener != null) {
                        List<Object> childOnOpListenerList = new ArrayList<>();
                        for (Object obj : childOnOpListener) {
                            if (obj instanceof Number) {
                                childOnOpListenerList.add(((Number) obj).longValue());
                            } else if (obj != null) {
                                childOnOpListenerList.add(obj.toString());
                            } else {
                                childOnOpListenerList.add(null);
                            }
                        }
                        childInfo.put("OnOpListener", childOnOpListenerList);
                    } else {
                        childInfo.put("OnOpListener", null);
                    }
                    if (child.getItemId() > 0) {
                        childInfo.put("itemId", child.getItemId());
                        childInfo.put("quantity", child.getItemQuantity());
                    }
                    childInfo.put("spriteId", child.getSpriteId());
                    Rectangle childBounds = child.getBounds();
                    if (childBounds != null) {
                        Map<String, Integer> childBoundInfo = new HashMap<>();
                        childBoundInfo.put("x", childBounds.x);
                        childBoundInfo.put("y", childBounds.y);
                        childBoundInfo.put("width", childBounds.width);
                        childBoundInfo.put("height", childBounds.height);
                        childInfo.put("bounds", childBoundInfo);
                        if (childBounds.width > 0 && childBounds.height > 0) {
                            Map<String, Integer> childRandomPoint = getRandomPointInRectangle(
                                    childBounds.x, childBounds.y,
                                    childBounds.width, childBounds.height, random);
                            if (childRandomPoint != null) {
                                childInfo.put("random_clickpoint", childRandomPoint);
                            }
                        }
                    }
                    children.add(childInfo);
                }
                widgetInfo.put("children", children);
            } else {
                widgetInfo.put("children", new ArrayList<>());
            }
            widgetData.put("widget", widgetInfo);
            log.debug("Found widget at ({}, {}): {}", x, y, widgetInfo);
        } else {
            widgetData.put("error", "No widget found at coordinates (" + x + ", " + y + ")");
            log.warn("No widget found at coordinates ({}, {})", x, y);
        }
        return widgetData;
    }

    private Widget findWidgetAtPoint(Point point) {
        for (int groupId = 0; groupId < 1000; groupId++) {
            for (int childId = 0; childId < 2000; childId++) {
                Widget widget = client.getWidget(groupId, childId);
                if (widget != null && !widget.isHidden()) {
                    int x = widget.getRelativeX();
                    int y = widget.getRelativeY();
                    int width = widget.getWidth();
                    int height = widget.getHeight();
                    if (width > 0 && height > 0 && x <= point.x && point.x <= x + width && y <= point.y && point.y <= y + height) {
                        return widget;
                    }
                    if (widget.getDynamicChildren() != null) {
                        for (Widget child : widget.getDynamicChildren()) {
                            if (child != null && !child.isHidden()) {
                                int childX = child.getRelativeX() + x;
                                int childY = child.getRelativeY() + y;
                                int childWidth = child.getWidth();
                                int childHeight = child.getHeight();
                                if (childWidth > 0 && childHeight > 0 && childX <= point.x && point.x <= childX + childWidth &&
                                        childY <= point.y && point.y <= childY + childHeight) {
                                    return child;
                                }
                            }
                        }
                    }
                }
            }
        }
        return null;
    }

    private Object handleInteractOptionsRequest() {
        List<Map<String, Object>> optionsList = new ArrayList<>();
        MenuEntry[] menuEntries = client.getMenuEntries();
        if (menuEntries == null || menuEntries.length == 0) {
            return optionsList;
        }

        int middleX;
        int currentY;

        boolean menuOpen = client.isMenuOpen();
        if (menuOpen) {
            // Exact when menu is open — this is used for all context clicks
            middleX = client.getMenuX() + (client.getMenuWidth() / 2);
            currentY = client.getMenuY() + 12;  // Tuned offset: first middle at ~getMenuY() + 12 (matches your log: 127 + 12 ≈ 139)
            log.debug("Menu open - getMenuY(): {}, getMenuX(): {}, width: {}", client.getMenuY(), client.getMenuX(), client.getMenuWidth());
        } else {
            // Fallback for hover/top-option check only (never used for context clicks)
            net.runelite.api.Point mousePos = client.getMouseCanvasPosition();
            middleX = mousePos.getX();
            currentY = mousePos.getY() + 20;  // Approximate — doesn't matter for context options
        }

        final int OPTION_HEIGHT = 15;  // Fixed in OSRS

        // IMPORTANT: Reverse iteration so top/visual-first option (default action, e.g. "Cage") gets lowest y (top of menu)
        // This fixes the current reversed labeling in your logs
        for (int i = menuEntries.length - 1; i >= 0; i--) {
            MenuEntry entry = menuEntries[i];
            int middleY = currentY + 7;  // Approximate center of 15px option height (7-8px down from top of slot)

            Map<String, Object> optionData = new HashMap<>();
            optionData.put("option", entry.getOption());
            optionData.put("target", entry.getTarget());
            optionData.put("middle_point", Map.of("x", middleX, "y", middleY));
            optionsList.add(optionData);

            currentY += OPTION_HEIGHT;
        }

        return optionsList;
    }
}