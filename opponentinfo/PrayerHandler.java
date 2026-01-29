// PrayerHandler.java
package net.runelite.client.plugins.asd;

import net.runelite.api.Client;
import net.runelite.api.Prayer;
import javax.inject.Inject;
import java.util.HashMap;
import java.util.Map;

public class PrayerHandler {
    @Inject
    private Client client;

    public Map<String, Boolean> getActivePrayers() {
        Map<String, Boolean> activePrayers = new HashMap<>();
        for (Prayer prayer : Prayer.values()) {
            int varbitId = prayer.getVarbit();
            boolean isActive = client.getVarbitValue(varbitId) == 1;
            activePrayers.put(prayer.name(), isActive);
        }
        return activePrayers;
    }

    public Map<String, Integer> getVarbitValues(Map<String, Object> requestedVarbits) {
        Map<String, Integer> varbitValues = new HashMap<>();
        for (Map.Entry<String, Object> entry : requestedVarbits.entrySet()) {
            try {
                int varbitId = Integer.parseInt(entry.getKey());
                int value = client.getVarbitValue(varbitId);
                varbitValues.put(String.valueOf(varbitId), value);
            } catch (NumberFormatException e) {
                // Log or handle invalid Varbit IDs if needed
            }
        }
        return varbitValues;
    }
}