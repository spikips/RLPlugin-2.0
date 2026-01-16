package net.runelite.client.plugins.asd;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.GameState;
import net.runelite.api.Point;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Singleton
public class LogoutHandler {
    @Inject
    private Client client;

    public Object handle(String function, Map<String, Object> params) {
        if (!"logout".equals(function)) {
            return "Invalid function for LogoutHandler";
        }

        GameState gameState = client.getGameState();
        log.info("Current game state: {}", gameState);

        Map<String, Object> widgetsData = new HashMap<>();
        widgetsData.put("game_state", gameState.name());

        if (gameState == GameState.LOGIN_SCREEN || gameState == GameState.LOGIN_SCREEN_AUTHENTICATOR) {
            // Try click-to-play screen (group 378)
            Widget clickToPlayRoot = client.getWidget(378, 0);
            if (clickToPlayRoot != null) {
                List<Map<String, Object>> allChildren = new ArrayList<>();
                collectAllWidgets(clickToPlayRoot, allChildren, 0);
                widgetsData.put("click_to_play_widgets", allChildren);
            }

            // Try login form/auth (group 596)
            Widget loginFormRoot = client.getWidget(596, 0);
            if (loginFormRoot != null) {
                List<Map<String, Object>> allChildren = new ArrayList<>();
                collectAllWidgets(loginFormRoot, allChildren, 0);
                widgetsData.put("login_form_widgets", allChildren);
            }

            // World select (group 69)
            Widget worldSelectRoot = client.getWidget(69, 0);
            if (worldSelectRoot != null) {
                List<Map<String, Object>> allWorldChildren = new ArrayList<>();
                collectAllWidgets(worldSelectRoot, allWorldChildren, 0);
                widgetsData.put("world_select_widgets", allWorldChildren);
            }

            // Specific known widgets
            Widget clickToPlayScreen = client.getWidget(WidgetInfo.LOGIN_CLICK_TO_PLAY_SCREEN);
            if (clickToPlayScreen != null) {
                widgetsData.put("click_to_play_screen", getWidgetData(clickToPlayScreen));
            }

            Widget motd = client.getWidget(WidgetInfo.LOGIN_CLICK_TO_PLAY_SCREEN_MESSAGE_OF_THE_DAY);
            if (motd != null) {
                widgetsData.put("message_of_the_day", getWidgetData(motd));
            }

        } else {
            // In-game logout (original)
            Widget worldSwitcher = client.getWidget(WidgetInfo.WORLD_SWITCHER_BUTTON);
            if (worldSwitcher != null) {
                widgetsData.put("world_switcher_button", getWidgetData(worldSwitcher));
            }

            Widget logoutButton = client.getWidget(WidgetInfo.LOGOUT_BUTTON);
            if (logoutButton != null) {
                widgetsData.put("logout_button", getWidgetData(logoutButton));
            }

            Widget logoutRoot = client.getWidget(182, 0);
            if (logoutRoot != null) {
                List<Map<String, Object>> allChildren = new ArrayList<>();
                collectAllWidgets(logoutRoot, allChildren, 0);
                widgetsData.put("logout_panel_widgets", allChildren);
            }

            Widget worldSwitcherRoot = client.getWidget(69, 0);
            if (worldSwitcherRoot != null) {
                List<Map<String, Object>> allWorldChildren = new ArrayList<>();
                collectAllWidgets(worldSwitcherRoot, allWorldChildren, 0);
                widgetsData.put("world_switcher_list_widgets", allWorldChildren);
            }

            Widget fixedLogoutTab = client.getWidget(WidgetInfo.FIXED_VIEWPORT_LOGOUT_TAB);
            if (fixedLogoutTab != null) {
                widgetsData.put("fixed_viewport_logout_tab", getWidgetData(fixedLogoutTab));
            }

            Widget resizableLogoutTab = client.getWidget(WidgetInfo.RESIZABLE_VIEWPORT_LOGOUT_TAB);
            if (resizableLogoutTab != null) {
                widgetsData.put("resizable_viewport_logout_tab", getWidgetData(resizableLogoutTab));
            }

            Widget resizableMinimapLogoutButton = client.getWidget(WidgetInfo.RESIZABLE_MINIMAP_LOGOUT_BUTTON);
            if (resizableMinimapLogoutButton != null) {
                widgetsData.put("resizable_minimap_logout_button", getWidgetData(resizableMinimapLogoutButton));
            }
        }

        if (widgetsData.size() <= 1) {
            return "No widgets found - ensure plugin loads at login with loadWhenOutdated = true";
        }

        return widgetsData;
    }

    private void collectAllWidgets(Widget widget, List<Map<String, Object>> collector, int depth) {
        if (widget == null) return;

        Map<String, Object> data = getWidgetData(widget);
        data.put("depth", depth);
        data.put("id", widget.getId());
        data.put("type", widget.getType());
        data.put("content_type", widget.getContentType());
        collector.add(data);

        if (widget.getDynamicChildren() != null) {
            for (Widget child : widget.getDynamicChildren()) {
                collectAllWidgets(child, collector, depth + 1);
            }
        }
        if (widget.getStaticChildren() != null) {
            for (Widget child : widget.getStaticChildren()) {
                collectAllWidgets(child, collector, depth + 1);
            }
        }
        if (widget.getNestedChildren() != null) {
            for (Widget child : widget.getNestedChildren()) {
                collectAllWidgets(child, collector, depth + 1);
            }
        }
    }

    private Map<String, Object> getWidgetData(Widget widget) {
        Map<String, Object> data = new HashMap<>();
        Point location = widget.getCanvasLocation();
        data.put("x", location.getX());
        data.put("y", location.getY());
        data.put("width", widget.getWidth());
        data.put("height", widget.getHeight());
        data.put("is_button", widget.getActions() != null && widget.getActions().length > 0);
        data.put("text", widget.getText() != null ? widget.getText() : "");
        data.put("hidden", widget.isHidden());
        return data;
    }
}