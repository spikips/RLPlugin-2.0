package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.*;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.client.game.ItemManager;
import net.runelite.client.plugins.opponentinfo.CustomOpponentInfoPlugin;
import net.runelite.client.util.Text;

import javax.inject.Inject;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
public class PlayerHandler implements RequestHandler {
    @Inject
    private Client client;

    @Inject
    private ItemManager itemManager;

    @Inject
    private Gson gson;

    private CustomOpponentInfoPlugin customOpponentInfoPlugin;

    public void setCustomOpponentInfoPlugin(CustomOpponentInfoPlugin customOpponentInfoPlugin) {
        this.customOpponentInfoPlugin = customOpponentInfoPlugin;
    }

    @Override
    public Object handle(String function, Map<String, Object> params) {
        switch (function) {
            case "player":
                return handlePlayerRequest(params);
            case "quest":
                return handleQuestRequest();
            case "stats":
                return handleStatsRequest();
            case "gear":
                return handleGearRequest();
            case "chat":
                return handleChatRequest();
            default:
                return new ResponseData().setError("Unknown player-related function: " + function);
        }
    }

    private Object handlePlayerRequest(Map<String, Object> params) {
        Map<String, Object> data = new HashMap<>();
        Player player = client.getLocalPlayer();
        if (player == null) {
            return data;
        }

        if (Boolean.TRUE.equals(params.get("location"))) {
            data.put("location", getPlayerLocation());
        }
        if (Boolean.TRUE.equals(params.get("health"))) {
            data.put("health", getPlayerHealth());
        }
        if (Boolean.TRUE.equals(params.get("prayer"))) {
            data.put("prayer", getPlayerPrayer());
        }
        if (Boolean.TRUE.equals(params.get("run"))) {
            data.put("runEnergy", getPlayerRunEnergy());
        }
        if (Boolean.TRUE.equals(params.get("weight"))) {
            data.put("weight", getPlayerWeight());
        }
        if (Boolean.TRUE.equals(params.get("animation"))) {
            data.put("animation", getPlayerAnimation());
        }
        if (Boolean.TRUE.equals(params.get("camera"))) {
            data.put("camera", getCameraInfo());
        }

        return data;
    }

    private Map<String, Integer> getPlayerLocation() {
        Player player = client.getLocalPlayer();
        if (player != null) {
            WorldPoint location = player.getWorldLocation();
            Map<String, Integer> locData = new HashMap<>();
            locData.put("x", location.getX());
            locData.put("y", location.getY());
            locData.put("plane", location.getPlane());
            return locData;
        }
        return null;
    }

    private Integer getPlayerHealth() {
        return client.getBoostedSkillLevel(Skill.HITPOINTS);
    }

    private Integer getPlayerPrayer() {
        return client.getBoostedSkillLevel(Skill.PRAYER);
    }

    private Integer getPlayerRunEnergy() {
        return client.getEnergy() / 100;
    }

    private Integer getPlayerWeight() {
        return client.getWeight();
    }

    private Integer getPlayerAnimation() {
        Player player = client.getLocalPlayer();
        if (player != null) {
            return player.getAnimation();
        }
        return null;
    }

    private Map<String, Object> getCameraInfo() {
        Map<String, Object> cameraData = new HashMap<>();
        cameraData.put("pitch", client.getCameraPitch());
        cameraData.put("yaw", client.getCameraYaw());
        cameraData.put("zoom", client.getScale());
        return cameraData;
    }

    private Object handleQuestRequest() {
        Map<String, String> questStates = new HashMap<>();
        for (Quest quest : Quest.values()) {
            QuestState state = quest.getState(client);
            questStates.put(quest.getName(), state.name());
        }
        return questStates;
    }

    private Object handleStatsRequest() {
        Map<String, Map<String, Integer>> stats = new HashMap<>();
        for (Skill skill : Skill.values()) {
            int level = client.getRealSkillLevel(skill);
            int xp = client.getSkillExperience(skill);
            Map<String, Integer> skillData = new HashMap<>();
            skillData.put("level", level);
            skillData.put("xp", xp);
            stats.put(skill.getName(), skillData);
        }
        return stats;
    }

    private Object handleGearRequest() {
        Map<String, Integer> gearData = new HashMap<>();
        ItemContainer equipment = client.getItemContainer(InventoryID.EQUIPMENT);
        if (equipment != null) {
            for (Item item : equipment.getItems()) {
                if (item.getId() != -1) {
                    String itemName = itemManager.getItemComposition(item.getId()).getName();
                    gearData.put(itemName, item.getId());
                }
            }
        }
        return gearData;
    }

    private Object handleChatRequest() {
        List<String> messages = new ArrayList<>();
        Widget chatbox = client.getWidget(WidgetInfo.CHATBOX_MESSAGE_LINES);
        if (chatbox != null && chatbox.getChildren() != null) {
            for (Widget widget : chatbox.getChildren()) {
                if (widget == null) continue;
                String message = widget.getText();
                if (message != null && !message.isEmpty()) {
                    messages.add(Text.removeTags(message));
                }
            }
        }
        return messages;
    }
}