// GetVarbits.java - Updated to support single ID query across Varbit, Varp (Varplayer), and VarClientInt
// Bulk mode remains Varbit-only for backward compatibility

package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.Varbits;

import javax.inject.Inject;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.HashMap;
import java.util.Map;

@Slf4j
public class GetVarbits {
    @Inject
    private Client client;

    private final Map<Integer, String> varbitNames = new HashMap<>();

    @Inject
    public GetVarbits() {
        populateVarbitNames();
    }

    private void populateVarbitNames() {
        try {
            for (Field field : Varbits.class.getFields()) {
                if (Modifier.isStatic(field.getModifiers()) && field.getType() == Integer.TYPE) {
                    int id = field.getInt(null);
                    varbitNames.put(id, field.getName());
                }
            }
            log.info("Populated {} varbit names", varbitNames.size());
        } catch (Exception e) {
            log.error("Failed to populate varbit names", e);
        }
    }

    public Map<String, Object> getVarbitValues(Map<String, Object> params) {
        Map<String, Object> response = new HashMap<>();

        if (params == null || params.isEmpty()) {
            response.put("error", "No parameters provided");
            return response;
        }

        // Single ID mode: {"id": 102}
        if (params.containsKey("id")) {
            int id;
            try {
                id = ((Number) params.get("id")).intValue();
            } catch (Exception e) {
                response.put("error", "Invalid 'id' parameter");
                return response;
            }

            Map<String, Object> values = new HashMap<>();
            values.put("varbit", client.getVarbitValue(id));
            values.put("varp", client.getVarpValue(id));        // Varplayer
            values.put("varcint", client.getVarcIntValue(id));  // VarClientInt

            Map<String, Object> result = new HashMap<>();
            result.put("id", id);
            result.put("values", values);

            // Optional: Add known Varbit name
            String name = varbitNames.getOrDefault(id, null);
            if (name != null) {
                result.put("name", name);
            }

            response.put("data", result);
            return response;
        }

        // Bulk mode (backward compatible - keys are string IDs, only Varbit values)
        Map<String, Integer> bulkValues = new HashMap<>();
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            try {
                int id = Integer.parseInt(entry.getKey());
                int value = client.getVarbitValue(id);
                bulkValues.put(String.valueOf(id), value);

                String name = varbitNames.getOrDefault(id, "Unknown");
                if (!name.equals("Unknown")) {
                    response.put("name_" + id, name);
                }
            } catch (NumberFormatException e) {
                log.warn("Invalid varbit ID: {}", entry.getKey());
            }
        }
        response.put("values", bulkValues);
        return response;
    }
}