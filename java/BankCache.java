package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.events.GameTick;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.game.ItemManager;

@Slf4j
@Singleton
public class BankCache {
    @Inject
    private Client client;

    @Inject
    private Gson gson;

    @Inject
    private ItemManager itemManager;

    private List<Map<String, Object>> previousData = new ArrayList<>();
    private final String filePath = "C:\\Users\\Asd\\source\\repos\\runelite_plugin\\modules\\fetch_data\\bank\\bank_items.json";

    @Subscribe
    public void onGameTick(GameTick event) {
        Widget bankMain = client.getWidget(WidgetInfo.BANK_CONTAINER);
        if (bankMain == null || bankMain.isHidden()) {
            return; // No action when closed—persist last data
        }

        Widget bankContainer = client.getWidget(WidgetInfo.BANK_ITEM_CONTAINER);
        if (bankContainer == null) {
            return;
        }

        List<Map<String, Object>> currentData = new ArrayList<>();
        Widget[] items = bankContainer.getDynamicChildren();
        for (int i = 0; i < items.length; i++) {
            Widget item = items[i];
            if (item.getItemId() > -1) {
                String name = itemManager.getItemComposition(item.getItemId()).getName();
                Map<String, Object> data = new HashMap<>();
                data.put("name", name);
                data.put("quantity", item.getItemQuantity());
                currentData.add(data);
            }
        }

        if (!currentData.equals(previousData)) {
            String currentJson = gson.toJson(currentData);
            try (FileWriter writer = new FileWriter(filePath)) {
                writer.write(currentJson);
                previousData = new ArrayList<>(currentData);
            } catch (IOException e) {
                log.error("Error writing bank items to file", e);
            }
        }
    }
}