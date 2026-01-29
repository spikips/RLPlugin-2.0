package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.GameState;
import net.runelite.api.Varbits;
import net.runelite.api.events.GameStateChanged;
import net.runelite.api.events.VarbitChanged;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.events.ConfigChanged;

import javax.inject.Inject;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Slf4j
public class VarbitHandler
{
    @Inject
    private Client client;

    @Inject
    private AsdConfig config;

    private final Set<Integer> includeSet = new HashSet<>();
    private final Set<Integer> excludeSet = new HashSet<>();

    private final Map<Integer, String> varbitNameMap = new HashMap<>();
    private final List<Map<String, Object>> varbitChanges = new ArrayList<>();
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();
    private final File jsonFile = new File("C:\\Users\\Asd\\source\\repos\\runelite_plugin\\modules\\varbits\\varbits.json");

    private GameState previousState = GameState.UNKNOWN;

    private void populateVarbitNames()
    {
        try
        {
            for (Field field : Varbits.class.getFields())
            {
                if (Modifier.isStatic(field.getModifiers()) && field.getType() == Integer.TYPE)
                {
                    int id = field.getInt(null);
                    varbitNameMap.put(id, field.getName());
                }
            }
            log.info("Populated {} varbit names", varbitNameMap.size());
        }
        catch (Exception e)
        {
            log.error("Failed to populate varbit names", e);
        }
    }

    private void initJson()
    {
        jsonFile.getParentFile().mkdirs();
        varbitChanges.clear();
        writeToFile();
        if (varbitNameMap.isEmpty())
        {
            populateVarbitNames();
        }
    }

    private void writeToFile()
    {
        synchronized (this)
        {
            try (FileWriter writer = new FileWriter(jsonFile))
            {
                writer.write(gson.toJson(varbitChanges));
            }
            catch (IOException e)
            {
                log.error("Failed to write varbits.json", e);
            }
        }
    }

    private void clearJson()
    {
        varbitChanges.clear();
        writeToFile();
        log.info("Cleared varbits.json content to empty array");
    }

    @Subscribe
    public void onGameStateChanged(GameStateChanged event)
    {
        GameState current = event.getGameState();
        if (previousState == GameState.LOGIN_SCREEN && current != GameState.LOGIN_SCREEN)
        {
            initJson();
        }
        if (current == GameState.LOGIN_SCREEN)
        {
            clearJson();
        }
        previousState = current;
    }

    @Subscribe
    public void onVarbitChanged(VarbitChanged event)
    {
        if (!config.varbitMonitoringEnabled())
        {
            return;
        }

        int varbitId = event.getVarbitId();
        if (varbitId < 0 || !shouldMonitor(varbitId))
        {
            return;
        }

        int value = client.getVarbitValue(varbitId);
        String name = varbitNameMap.getOrDefault(varbitId, "Unknown");

        // Fixed logging: conditional args
        if (config.enableVarbitNames() && !"Unknown".equals(name))
        {
            log.info("Varbit {} ({}) changed to: {}", varbitId, name, value);
        }
        else
        {
            log.info("Varbit ID: {} changed to value: {}", varbitId, value);
        }

        // Collect in memory
        Map<String, Object> changeData = new HashMap<>();
        changeData.put("tick", client.getTickCount());
        changeData.put("id", varbitId);
        changeData.put("value", value);
        if (!"Unknown".equals(name))
        {
            changeData.put("name", name);
        }
        varbitChanges.add(changeData);
        writeToFile();
    }

    @Subscribe
    public void onConfigChanged(ConfigChanged event)
    {
        if (!event.getGroup().equals("asd"))
        {
            return;
        }

        String key = event.getKey();
        switch (key)
        {
            case "varbitMonitoringEnabled":
            case "enableVarbitNames":
                // No action needed; checked inline
                break;
            case "includeVarbits":
            case "excludeVarbits":
                updateFilters();
                break;
        }
    }

    private boolean shouldMonitor(int varbitId)
    {
        boolean includeThis = includeSet.isEmpty() || includeSet.contains(varbitId);
        boolean excludeThis = excludeSet.contains(varbitId);
        return includeThis && !excludeThis;
    }

    public void updateFilters()
    {
        includeSet.clear();
        String includeStr = config.includeVarbits();
        if (!includeStr.isEmpty())
        {
            for (String s : includeStr.split(","))
            {
                s = s.trim();
                if (!s.isEmpty())
                {
                    try
                    {
                        includeSet.add(Integer.parseInt(s));
                    }
                    catch (NumberFormatException e)
                    {
                        log.warn("Invalid include varbit ID: {}", s);
                    }
                }
            }
        }

        excludeSet.clear();
        String excludeStr = config.excludeVarbits();
        if (!excludeStr.isEmpty())
        {
            for (String s : excludeStr.split(","))
            {
                s = s.trim();
                if (!s.isEmpty())
                {
                    try
                    {
                        excludeSet.add(Integer.parseInt(s));
                    }
                    catch (NumberFormatException e)
                    {
                        log.warn("Invalid exclude varbit ID: {}", s);
                    }
                }
            }
        }
    }
}