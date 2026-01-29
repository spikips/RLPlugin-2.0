package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
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
        Map<String, Integer> values = new HashMap<>();

        if (params == null || params.isEmpty()) {
            response.put("error", "No varbit IDs provided");
            return response;
        }

        for (Map.Entry<String, Object> entry : params.entrySet()) {
            try {
                int varbitId = Integer.parseInt(entry.getKey());
                int value = client.getVarbitValue(varbitId);
                values.put(String.valueOf(varbitId), value);

                String name = varbitNames.getOrDefault(varbitId, "Unknown");
                if (!name.equals("Unknown")) {
                    response.put("name_" + varbitId, name);  // Optional: include name
                }
            } catch (NumberFormatException e) {
                log.warn("Invalid varbit ID: {}", entry.getKey());
            }
        }

        response.put("values", values);
        return response;
    }
}