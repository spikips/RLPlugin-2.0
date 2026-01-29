// WeaponHandler.java
package net.runelite.client.plugins.asd;

import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Singleton
public class WeaponHandler {

    @Inject
    private Client client;

    private static final Map<Integer, Map<Integer, String>> STYLE_MAP = new HashMap<>();

    static {
        // Shared maps for common patterns

        // Pattern: Attack (0), Strength (1), Strength Crush (2), Defence (3)
        Map<Integer, String> crushPattern = new HashMap<>();
        crushPattern.put(0, "Attack");
        crushPattern.put(1, "Strength");
        crushPattern.put(2, "Strength Crush");
        crushPattern.put(3, "Defence");
        STYLE_MAP.put(10, crushPattern); // 2h sword
        STYLE_MAP.put(1, crushPattern); // Axe

        // Pattern: Attack (0), Strength (1), Defence (3)
        Map<Integer, String> basicMelee = new HashMap<>();
        basicMelee.put(0, "Attack");
        basicMelee.put(1, "Strength");
        basicMelee.put(3, "Defence");
        STYLE_MAP.put(2, basicMelee); // Blunt
        STYLE_MAP.put(17, basicMelee); // Stab Sword

        // Pattern: Shared (0,1,2), Defence (3)
        Map<Integer, String> sharedPattern = new HashMap<>();
        sharedPattern.put(0, "Shared");
        sharedPattern.put(1, "Shared");
        sharedPattern.put(2, "Shared");
        sharedPattern.put(3, "Defence");
        STYLE_MAP.put(15, sharedPattern); // Spear

        // Pattern: Attack (0), Strength (1), Shared (2), Defence (3)
        Map<Integer, String> spikedPattern = new HashMap<>();
        spikedPattern.put(0, "Attack");
        spikedPattern.put(1, "Strength");
        spikedPattern.put(2, "Shared");
        spikedPattern.put(3, "Defence");
        STYLE_MAP.put(16, spikedPattern); // Spiked
        STYLE_MAP.put(9, spikedPattern); // Slash Sword

        // Pattern: Accurate (0), Rapid (1), Defence (3)
        Map<Integer, String> thrownPattern = new HashMap<>();
        thrownPattern.put(0, "Accurate");
        thrownPattern.put(1, "Rapid");
        thrownPattern.put(3, "Defence");
        STYLE_MAP.put(19, thrownPattern); // Thrown

        // Pattern: Accurate (0,1), Defence (3)
        Map<Integer, String> poweredPattern = new HashMap<>();
        poweredPattern.put(0, "Accurate");
        poweredPattern.put(1, "Accurate");
        poweredPattern.put(3, "Defence");
        STYLE_MAP.put(24, poweredPattern); // Powered Staff

        // Pattern: Accurate (0), Rapid (1), Long Range (3)
        Map<Integer, String> crossbowPattern = new HashMap<>();
        crossbowPattern.put(0, "Accurate");
        crossbowPattern.put(1, "Rapid");
        crossbowPattern.put(3, "Long Range");
        STYLE_MAP.put(5, crossbowPattern); // Crossbow

        // Pattern: Attack (0), Shared (1), Defence (3)
        Map<Integer, String> whipPattern = new HashMap<>();
        whipPattern.put(0, "Attack");
        whipPattern.put(1, "Shared");
        whipPattern.put(3, "Defence");
        STYLE_MAP.put(20, whipPattern); // Whip

        // Pattern: Accurate (0), Rapid (1), Longrange (3)
        Map<Integer, String> bowPattern = new HashMap<>();
        bowPattern.put(0, "Accurate");
        bowPattern.put(1, "Rapid");
        bowPattern.put(3, "Longrange");
        STYLE_MAP.put(3, bowPattern); // Bow
    }

    public Map<String, String> getCurrentCombatInfo() {
        Map<String, String> info = new HashMap<>();
        int styleIndex = client.getVarpValue(43);
        int weaponType = client.getVarbitValue(357);
        String category = getWeaponCategory(weaponType);
        String style = "Unknown";
        boolean isAutocast = client.getVarbitValue(276) > 0;
        boolean isDefensive = client.getVarbitValue(2668) == 1;

        // Log for debugging
        log.info("WeaponType: " + weaponType + ", StyleIndex: " + styleIndex + ", Autocast: " + isAutocast + ", Defensive: " + isDefensive);

        Map<Integer, String> styles = STYLE_MAP.get(weaponType);
        if (styles != null) {
            style = styles.getOrDefault(styleIndex, "Unknown");
        } else if (weaponType == 18 || weaponType == 4) { // Staff (handle autocast separately)
            if (styleIndex == 4) {  // Autocast mode
                style = "Autocast";
                if (isDefensive) {
                    style += " Defensive (Magic/Defence)";
                } else {
                    style += " Standard (Magic)";
                }
            } else {
                // Use basicMelee for non-autocast
                style = STYLE_MAP.get(2).getOrDefault(styleIndex, "Unknown"); // Reuse blunt pattern
            }
        }

        info.put("category", category);
        info.put("style", style);
        return info;
    }

    private String getWeaponCategory(int type) {
        switch (type) {
            case 10: return "2h Sword";
            case 1: return "Axe";
            case 2: return "Blunt";
            case 15: return "Spear";
            case 16: return "Spiked";
            case 19: return "Thrown";
            case 24: return "Powered Staff";
            case 5: return "Crossbow";
            case 20: return "Whip";
            case 9: return "Slash Sword";
            case 3: return "Bow";
            case 4:
            case 18: return "Staff";
            case 17: return "Stab Sword";
            default: return "Unknown";
        }
    }
}